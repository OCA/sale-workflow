# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_plan_method = fields.Selection(
        selection=[
            ("proportional", "Proportional"),
            ("sequential", "Sequential Grouped"),
            ("manual", "Manual"),
        ],
        default="proportional",
        required=True,
        copy=False,
    )

    def _uses_invoice_plan_allocation(self):
        self.ensure_one()
        return self.use_invoice_plan and self.invoice_plan_method in (
            "manual",
            "sequential",
        )

    def _get_invoice_plan_allocatable_lines(self):
        self.ensure_one()
        return self.order_line.filtered(
            lambda line: not line.display_type
            and line.product_id
            and not line.is_downpayment
        )

    def _get_sequential_line_groups(self):
        """Group allocatable lines by ``invoice_plan_group``, ascending."""
        self.ensure_one()
        groups = defaultdict(list)
        for line in self._get_invoice_plan_allocatable_lines():
            groups[line.invoice_plan_group].append(line)
        return {group: groups[group] for group in sorted(groups)}

    def _get_sequential_num_installment(self):
        """Sequential: total installments = sum of max(qty) per line group."""
        self.ensure_one()
        self._validate_sequential_quantities()
        groups = self._get_sequential_line_groups()
        return sum(
            round(max(line.product_uom_qty for line in group))
            for group in groups.values()
        )

    def _validate_sequential_quantities(self):
        """Sequential allocation requires positive integer quantities."""
        self.ensure_one()
        sale_lines = self._get_invoice_plan_allocatable_lines()
        if not sale_lines:
            raise ValidationError(
                self.env._(
                    "The 'Sequential Grouped' method requires at least "
                    "one invoiceable sales order line."
                )
            )
        for line in sale_lines:
            rounding = line.product_uom.rounding
            quantity = line.product_uom_qty
            if float_compare(quantity, 0.0, precision_rounding=rounding) != 1:
                raise ValidationError(
                    self.env._(
                        "The 'Sequential Grouped' method requires positive "
                        "quantities. Line %(line)s has quantity %(qty)s."
                    )
                    % {"line": line.name, "qty": quantity}
                )
            if not float_is_zero(
                quantity - round(quantity), precision_rounding=rounding
            ):
                raise ValidationError(
                    self.env._(
                        "The 'Sequential Grouped' method requires integer "
                        "quantities. Line %(line)s has quantity %(qty)s."
                    )
                    % {"line": line.name, "qty": quantity}
                )

    def _prepare_invoice_plan_allocations(self):
        Allocation = self.env["sale.invoice.plan.allocation"]
        for order in self.filtered(
            lambda sale: sale.invoice_plan_method in ("manual", "sequential")
        ):
            sale_lines = order._get_invoice_plan_allocatable_lines()
            plans = order.invoice_plan_ids.filtered(
                lambda invoice_plan: invoice_plan.invoice_type == "installment"
                and not invoice_plan.invoiced
            )
            if order.invoice_plan_method == "sequential":
                order._auto_allocate_sequential(plans)
                continue
            # Manual mode: batch-create the empty rows the user will fill in.
            vals_list = [
                {"plan_id": plan.id, "sale_line_id": sale_line.id}
                for plan in plans
                for sale_line in sale_lines - plan.allocation_ids.sale_line_id
            ]
            if vals_list:
                Allocation.create(vals_list)

    def _auto_allocate_sequential(self, plans):
        """Bulk-rebuild open allocations: 1 unit per line and installment per group."""
        self.ensure_one()
        if not plans:
            return
        installment_plans = self.invoice_plan_ids.filtered(
            lambda plan: plan.invoice_type == "installment"
        )
        expected_count = self._get_sequential_num_installment()
        if len(installment_plans) != expected_count:
            raise ValidationError(
                self.env._(
                    "The sequential allocation now requires %(expected)s "
                    "installments, but the invoice plan has %(actual)s. Remove "
                    "and recreate the invoice plan."
                )
                % {"expected": expected_count, "actual": len(installment_plans)}
            )
        # Absolute schedule; only replace open plans, preserving invoiced ones.
        plan_by_number = {plan.installment: plan for plan in installment_plans}
        open_plan_ids = set(plans.ids)
        vals_list = []
        global_installment = 0
        for group_lines in self._get_sequential_line_groups().values():
            group_size = round(max(line.product_uom_qty for line in group_lines))
            for installment_offset in range(group_size):
                plan = plan_by_number.get(global_installment + 1)
                if plan and plan.id in open_plan_ids:
                    for line in group_lines:
                        if installment_offset < round(line.product_uom_qty):
                            vals_list.append(
                                {
                                    "plan_id": plan.id,
                                    "sale_line_id": line.id,
                                    "quantity": 1.0,
                                }
                            )
                global_installment += 1
        plans.allocation_ids.unlink()
        if vals_list:
            self.env["sale.invoice.plan.allocation"].create(vals_list)

    def _validate_invoice_plan_allocations(self, invoiceable_plan=False):
        for order in self.filtered(lambda sale: sale._uses_invoice_plan_allocation()):
            plans = order.invoice_plan_ids.filtered(
                lambda plan: plan.invoice_type == "installment"
            )
            plans._validate_allocation()
            planned_by_line = defaultdict(float)
            for allocation in plans.allocation_ids:
                planned_by_line[allocation.sale_line_id] += allocation.quantity
            for sale_line in order._get_invoice_plan_allocatable_lines():
                planned_qty = planned_by_line[sale_line]
                if (
                    float_compare(
                        planned_qty,
                        sale_line.product_uom_qty,
                        precision_rounding=sale_line.product_uom.rounding,
                    )
                    != 0
                ):
                    raise ValidationError(
                        self.env._(
                            "The total planned quantity for %(line)s must equal "
                            "the ordered quantity. Planned: %(planned)s, "
                            "Ordered: %(ordered)s"
                        )
                        % {
                            "line": sale_line.name,
                            "planned": planned_qty,
                            "ordered": sale_line.product_uom_qty,
                        }
                    )
            if invoiceable_plan:
                invoiceable_plan._validate_allocation(check_invoiceable=True)

    def action_allocate_evenly(self):
        """Split remaining quantities evenly over open installments."""
        Allocation = self.env["sale.invoice.plan.allocation"]
        for order in self.filtered(lambda sale: sale.invoice_plan_method == "manual"):
            plans = order.invoice_plan_ids.filtered(
                lambda plan: plan.invoice_type == "installment" and not plan.invoiced
            ).sorted("installment")
            if not plans:
                continue
            count = len(plans)
            vals_list = []
            invoiced_plans = order.invoice_plan_ids.filtered(
                lambda plan: plan.invoice_type == "installment" and plan.invoiced
            )
            invoiced_by_line = defaultdict(float)
            for allocation in invoiced_plans.allocation_ids:
                invoiced_by_line[allocation.sale_line_id] += allocation.quantity
            for sale_line in order._get_invoice_plan_allocatable_lines():
                rounding = sale_line.product_uom.rounding
                invoiced_plan_qty = invoiced_by_line[sale_line]
                quantity = sale_line.product_uom_qty - invoiced_plan_qty
                if float_compare(quantity, 0.0, precision_rounding=rounding) == -1:
                    raise ValidationError(
                        self.env._(
                            "The invoiced allocation for %(line)s exceeds its "
                            "ordered quantity."
                        )
                        % {"line": sale_line.name}
                    )
                allocated = 0.0
                for index, plan in enumerate(plans):
                    if index == count - 1:
                        plan_qty = float_round(
                            quantity - allocated, precision_rounding=rounding
                        )
                    else:
                        plan_qty = float_round(
                            quantity / count, precision_rounding=rounding
                        )
                        allocated += plan_qty
                    vals_list.append(
                        {
                            "plan_id": plan.id,
                            "sale_line_id": sale_line.id,
                            "quantity": plan_qty,
                        }
                    )
            plans.allocation_ids.unlink()
            if vals_list:
                Allocation.create(vals_list)
        return True

    def action_view_invoice_plan_allocations(self):
        """Open all line allocations in a single editable, grouped list."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Invoice Plan Line Allocations"),
            "res_model": "sale.invoice.plan.allocation",
            "view_mode": "list",
            "view_id": self.env.ref(
                "sale_invoice_plan_allocation."
                "view_sale_invoice_plan_allocation_grid_list"
            ).id,
            "domain": [("sale_id", "=", self.id)],
            "context": {"group_by": "installment"},
        }

    def create_invoice_plan(
        self, num_installment, installment_date, interval, interval_type, advance
    ):
        self.ensure_one()
        if self.invoice_plan_method == "sequential":
            # The derived count replaces the value from the wizard.
            num_installment = self._get_sequential_num_installment()
        result = super().create_invoice_plan(
            num_installment,
            installment_date,
            interval,
            interval_type,
            advance,
        )
        self._prepare_invoice_plan_allocations()
        return result

    def action_confirm(self):
        self._validate_invoice_plan_allocations()
        return super().action_confirm()

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoice_plan_id = self.env.context.get("invoice_plan_id")
        if invoice_plan_id:
            plan = self.env["sale.invoice.plan"].browse(invoice_plan_id).exists()
            if plan and plan.allocation_method in ("manual", "sequential"):
                plan.sale_id._validate_invoice_plan_allocations(invoiceable_plan=plan)
        return super()._create_invoices(grouped=grouped, final=final, date=date)

    def write(self, vals):
        if "invoice_plan_method" in vals:
            changing_orders = self.filtered(
                lambda order: order.invoice_plan_method != vals["invoice_plan_method"]
            )
            if changing_orders.invoice_plan_ids:
                raise UserError(
                    self.env._(
                        "The invoice plan method cannot be changed after an invoice "
                        "plan has been created. Remove the invoice plan first."
                    )
                )
        result = super().write(vals)
        if vals.get("invoice_plan_method") in ("manual", "sequential"):
            self._prepare_invoice_plan_allocations()
        elif vals.get("invoice_plan_method") == "proportional":
            self.invoice_plan_ids.allocation_ids.unlink()
        return result
