# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class SaleInvoicePlan(models.Model):
    _inherit = "sale.invoice.plan"

    allocation_method = fields.Selection(
        related="sale_id.invoice_plan_method",
        string="Allocation Method",
    )
    allocation_ids = fields.One2many(
        comodel_name="sale.invoice.plan.allocation",
        inverse_name="plan_id",
        string="Line Allocations",
        copy=False,
    )
    currency_id = fields.Many2one(related="sale_id.currency_id")
    allocated_amount = fields.Monetary(
        compute="_compute_allocation_amounts",
        string="Allocated",
    )
    amount_to_allocate = fields.Monetary(
        compute="_compute_allocation_amounts",
        string="Balance",
    )

    @api.depends("allocation_ids.amount", "amount")
    def _compute_allocation_amounts(self):
        for plan in self:
            plan.allocated_amount = sum(plan.allocation_ids.mapped("amount"))
            plan.amount_to_allocate = plan.amount - plan.allocated_amount

    def _uses_line_allocation(self):
        self.ensure_one()
        return (
            self.allocation_method in ("manual", "sequential")
            and self.invoice_type == "installment"
        )

    @api.depends("percent", "allocation_ids.amount")
    def _compute_amount(self):
        """Sequential mode: amount and percent derive from the allocations."""
        sequential = self.filtered(
            lambda plan: plan.allocation_method == "sequential"
            and plan.invoice_type == "installment"
            and not plan.invoiced
        )
        for plan in sequential:
            amount_untaxed = plan.sale_id._origin.amount_untaxed
            allocated = plan.currency_id.round(
                sum(plan.allocation_ids.mapped("amount"))
            )
            plan.amount = allocated
            plan.percent = allocated / amount_untaxed * 100 if amount_untaxed else 0.0
        # Base behavior for proportional/manual/advance/invoiced plans.
        return super(SaleInvoicePlan, self - sequential)._compute_amount()

    def action_prepare_allocations(self):
        self.ensure_one()
        self.sale_id._prepare_invoice_plan_allocations()
        # Re-open the dialog so the refreshed allocations are shown.
        return self._get_allocation_dialog_action()

    def _get_allocation_dialog_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Allocate Installment %s") % self.installment,
            "res_model": "sale.invoice.plan",
            "res_id": self.id,
            "view_mode": "form",
            "view_id": self.env.ref(
                "sale_invoice_plan_allocation.view_sale_invoice_plan_form_allocation"
            ).id,
            "target": "new",
        }

    def action_open_allocation(self):
        self.ensure_one()
        return self._get_allocation_dialog_action()

    def _validate_allocation(self, check_invoiceable=False):
        for plan in self.filtered(
            lambda invoice_plan: invoice_plan._uses_line_allocation()
        ):
            allocations = plan.allocation_ids.filtered("quantity")
            if not allocations:
                raise ValidationError(
                    self.env._("Installment %(installment)s has no allocated quantity.")
                    % {"installment": plan.installment}
                )
            # Manual mode requires allocated == target; sequential instead checks
            # per-line totals against ordered quantities on sale.order.
            if plan.allocation_method == "manual" and not plan.currency_id.is_zero(
                plan.amount_to_allocate
            ):
                raise ValidationError(
                    self.env._(
                        "Installment %(installment)s must be fully allocated. "
                        "Target: %(target)s, Allocated: %(allocated)s, "
                        "Balance: %(balance)s"
                    )
                    % {
                        "installment": plan.installment,
                        "target": plan.amount,
                        "allocated": plan.allocated_amount,
                        "balance": plan.amount_to_allocate,
                    }
                )
            if not check_invoiceable:
                continue
            for allocation in allocations:
                sale_line = allocation.sale_line_id
                if (
                    float_compare(
                        allocation.quantity,
                        sale_line.qty_to_invoice,
                        precision_rounding=sale_line.product_uom.rounding,
                    )
                    == 1
                ):
                    raise ValidationError(
                        self.env._(
                            "The planned quantity for %(line)s exceeds the "
                            "quantity available to invoice. Planned: %(planned)s, "
                            "Available: %(available)s"
                        )
                        % {
                            "line": sale_line.name,
                            "planned": allocation.quantity,
                            "available": sale_line.qty_to_invoice,
                        }
                    )

    def _get_plan_qty(self, order_line, percent):
        self.ensure_one()
        if not self._uses_line_allocation():
            return super()._get_plan_qty(order_line, percent)
        allocation = self.allocation_ids.filtered(
            lambda line: line.sale_line_id == order_line
        )
        return allocation.quantity if allocation else 0.0

    def _compute_new_invoice_quantity(self, invoice_move):
        self.ensure_one()
        if not self._uses_line_allocation():
            return super()._compute_new_invoice_quantity(invoice_move)

        move = invoice_move.with_context(check_move_validity=False)
        for line in move.invoice_line_ids.filtered(
            lambda invoice_line: invoice_line.display_type
            not in ("line_section", "line_note")
        ):
            order_line = fields.first(line.sale_line_ids)
            if order_line and order_line.is_downpayment:
                if not self.last:
                    self._update_new_quantity(line, self.percent)
                continue
            plan_qty = order_line and self._get_plan_qty(order_line, self.percent)
            if plan_qty:
                self._update_new_quantity(line, self.percent)
            else:
                line.unlink()
        move.line_ids.filtered(
            lambda line: line.display_type
            not in ("product", "line_section", "line_note", "payment_term", "tax")
        ).unlink()


class SaleInvoicePlanAllocation(models.Model):
    _name = "sale.invoice.plan.allocation"
    _description = "Sales Invoice Plan Line Allocation"
    _order = "plan_id, sale_line_id"

    plan_id = fields.Many2one(
        comodel_name="sale.invoice.plan",
        string="Invoice Plan",
        required=True,
        index=True,
        ondelete="cascade",
    )
    sale_id = fields.Many2one(
        related="plan_id.sale_id",
        string="Sales Order",
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        related="sale_id.company_id",
        store=True,
        index=True,
    )
    installment = fields.Integer(
        related="plan_id.installment",
        string="Installment",
        store=True,
        index=True,
    )
    plan_date = fields.Date(
        related="plan_id.plan_date",
        string="Plan Date",
        store=True,
    )
    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sales Order Line",
        required=True,
        index=True,
        ondelete="cascade",
        domain="[('order_id', '=', sale_id), ('display_type', '=', False)]",
    )
    product_id = fields.Many2one(related="sale_line_id.product_id", store=True)
    product_uom_id = fields.Many2one(related="sale_line_id.product_uom")
    ordered_quantity = fields.Float(
        related="sale_line_id.product_uom_qty",
        string="Ordered",
    )
    quantity = fields.Float(
        string="This Installment",
        digits="Product Unit of Measure",
    )
    currency_id = fields.Many2one(related="sale_id.currency_id")
    amount = fields.Monetary(
        compute="_compute_amount",
        string="Untaxed Amount",
        store=True,
    )
    no_edit = fields.Boolean(related="plan_id.no_edit")

    _sql_constraints = [
        (
            "unique_plan_sale_line",
            "UNIQUE(plan_id, sale_line_id)",
            "A sales order line can only be allocated once per installment.",
        )
    ]

    @api.depends("quantity", "sale_line_id.price_reduce_taxexcl")
    def _compute_amount(self):
        for allocation in self:
            allocation.amount = allocation.currency_id.round(
                allocation.quantity * allocation.sale_line_id.price_reduce_taxexcl
            )

    @api.constrains("plan_id", "sale_line_id")
    def _check_sale_line_order(self):
        for allocation in self:
            if allocation.sale_line_id.order_id != allocation.sale_id:
                raise ValidationError(
                    self.env._(
                        "The allocated sales order line must belong to the invoice "
                        "plan's sales order."
                    )
                )
            if allocation.sale_line_id.display_type:
                raise ValidationError(
                    self.env._(
                        "Sections and notes cannot be allocated to an invoice plan."
                    )
                )
            if not allocation.sale_line_id.product_id:
                raise ValidationError(
                    self.env._("An allocated sales order line must have a product.")
                )
            if allocation.sale_line_id.is_downpayment:
                raise ValidationError(
                    self.env._("Down payment lines cannot be allocated manually.")
                )

    @api.constrains("quantity")
    def _check_quantity(self):
        for allocation in self:
            if (
                float_compare(
                    allocation.quantity,
                    0.0,
                    precision_rounding=allocation.product_uom_id.rounding,
                )
                == -1
            ):
                raise ValidationError(
                    self.env._("The allocated quantity cannot be negative.")
                )

    def _check_plan_editable(self):
        if self.mapped("plan_id").filtered("invoiced"):
            raise UserError(
                self.env._("An allocation cannot be changed after invoicing its plan.")
            )

    @api.model_create_multi
    def create(self, vals_list):
        plans = self.env["sale.invoice.plan"].browse(
            [vals["plan_id"] for vals in vals_list if vals.get("plan_id")]
        )
        if plans.filtered("invoiced"):
            raise UserError(
                self.env._("An allocation cannot be added after invoicing its plan.")
            )
        return super().create(vals_list)

    def write(self, vals):
        self._check_plan_editable()
        return super().write(vals)

    def unlink(self):
        self._check_plan_editable()
        return super().unlink()
