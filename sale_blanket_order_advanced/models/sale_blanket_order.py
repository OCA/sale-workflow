# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round


class SaleBlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    sale_order_plan_ids = fields.One2many(
        comodel_name="blanket.order.plan",
        inverse_name="sale_id",
        string="Sale Order Plan",
        copy=False,
    )
    use_sale_order_plan = fields.Boolean(
        default=lambda self: self._default_use_sale_order_plan(),
        copy=False,
    )
    enable_product_costs = fields.Boolean(
        default=lambda self: self._default_enable_product_costs(),
        copy=False,
    )
    enable_service_costs = fields.Boolean(
        default=lambda self: self._default_enable_service_costs(),
        copy=False,
    )
    enable_version_control = fields.Boolean(
        default=lambda self: self._default_enable_version_control(),
        copy=False,
    )

    def _default_use_sale_order_plan(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_blanket_order_advanced.use_sale_order_plan", "False")
            == "True"
        )

    def _default_enable_product_costs(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_blanket_order_advanced.enable_product_costs", "False")
            == "True"
        )

    def _default_enable_service_costs(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_blanket_order_advanced.enable_service_costs", "False")
            == "True"
        )

    def _default_enable_version_control(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_blanket_order_advanced.enable_version_control", "True")
            != "False"
        )

    ip_sale_order_plan = fields.Boolean(
        string="Sale Order Plan In Process",
        compute="_compute_ip_sale_order_plan",
        help="At least one order plan line pending to create sale order",
    )
    order_product_ids = fields.One2many(
        "blanket.order.product",
        "blanket_order_id",
        string="Blanket Order Products Costs",
    )

    order_service_ids = fields.One2many(
        "blanket.order.service",
        "blanket_order_id",
        string="Blanket Order Services Costs",
    )

    total_product_costs = fields.Monetary(
        "Total Product Cost Target", compute="_compute_total_product_costs"
    )

    total_service_costs = fields.Monetary(
        "Total Service Cost Target", compute="_compute_total_service_costs"
    )

    total_costs = fields.Monetary(
        string="Total Cost Target (Products Costs + Services Costs)",
        compute="_compute_total_costs",
        store=True,
    )

    account_analytic_line_ids = fields.One2many(
        comodel_name="account.analytic.line",
        compute="_compute_account_analytic_line_ids",
        string="Analytic Line",
    )

    account_analytic_line_count = fields.Integer(
        compute="_compute_account_analytic_line_ids",
    )

    version_ids = fields.One2many(
        comodel_name="sale.blanket.order.advanced.version.wizard",
        inverse_name="old_blanket_order_id",
        string="Versions",
    )
    version_count = fields.Integer(
        compute="_compute_version_count",
    )

    all_sale_orders_invoiced = fields.Boolean(
        compute="_compute_all_sale_orders_invoiced",
    )
    order_plan_count = fields.Integer(
        compute="_compute_order_plan_count",
    )
    product_cost_count = fields.Integer(
        compute="_compute_product_cost_count",
    )
    service_cost_count = fields.Integer(
        compute="_compute_service_cost_count",
    )

    def _compute_all_sale_orders_invoiced(self):
        for record in self:
            sale_orders = record.mapped("line_ids.sale_lines.order_id")
            if sale_orders:
                record.all_sale_orders_invoiced = all(
                    so.invoice_status == "invoiced" for so in sale_orders
                )
            else:
                record.all_sale_orders_invoiced = False

    def _compute_account_analytic_line_ids(self):
        for rec in self:
            account_analytic_line = self.env["account.analytic.line"]
            account_analytic_lines = account_analytic_line.search(
                [
                    ("account_id", "=", rec.analytic_account_id.id),
                ]
            )
            rec.account_analytic_line_ids = account_analytic_lines
            rec.account_analytic_line_count = len(rec.account_analytic_line_ids)

    def _compute_ip_sale_order_plan(self):
        for rec in self:
            has_order_plan = rec.use_sale_order_plan and rec.sale_order_plan_ids
            to_order = rec.sale_order_plan_ids.filtered(lambda line: not line.ordered)
            if rec.state == "open" and has_order_plan and to_order:
                rec.ip_sale_order_plan = True
                continue
            rec.ip_sale_order_plan = False

    @api.depends("version_ids")
    def _compute_version_count(self):
        for record in self:
            record.version_count = len(record.version_ids)

    @api.depends("sale_order_plan_ids")
    def _compute_order_plan_count(self):
        for record in self:
            record.order_plan_count = len(record.sale_order_plan_ids)

    @api.depends("order_product_ids")
    def _compute_product_cost_count(self):
        for record in self:
            record.product_cost_count = len(record.order_product_ids)

    @api.depends("order_service_ids")
    def _compute_service_cost_count(self):
        for record in self:
            record.service_cost_count = len(record.order_service_ids)

    @api.constrains("state")
    def _check_order_plan(self):
        for rec in self:
            if rec.state != "draft":
                if rec.sale_order_plan_ids.filtered(lambda line: not line.percent):
                    raise ValidationError(
                        _("Please fill percentage for all order plan lines")
                    )

    def action_confirm(self):
        if self.filtered(lambda r: r.use_sale_order_plan and not r.sale_order_plan_ids):
            raise UserError(_("Use Order Plan selected, but no plan created"))
        return super().action_confirm()

    def create_order_plan(
        self, num_installment, installment_date, interval, interval_type
    ):
        self.ensure_one()
        self.sale_order_plan_ids.unlink()
        order_plans = []
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Product Unit of Measure")
        percent = float_round(1.0 / num_installment * 100, prec)
        percent_last = 100 - (percent * (num_installment - 1))
        for i in range(num_installment):
            this_installment = i + 1
            if num_installment == this_installment:
                percent = percent_last
            vals = {
                "installment": this_installment,
                "plan_date": installment_date,
                "order_type": "installment",
                "percent": percent,
            }
            order_plans.append((0, 0, vals))
            installment_date = self._next_date(
                installment_date, interval, interval_type
            )
        self.write({"sale_order_plan_ids": order_plans})
        return True

    def remove_order_plan(self):
        self.ensure_one()
        self.sale_order_plan_ids.unlink()
        return True

    @api.model
    def _next_date(self, installment_date, interval, interval_type):
        installment_date = fields.Date.from_string(installment_date)
        if interval_type == "month":
            next_date = installment_date + relativedelta(months=+interval)
        elif interval_type == "year":
            next_date = installment_date + relativedelta(years=+interval)
        else:
            next_date = installment_date + relativedelta(days=+interval)
        next_date = fields.Date.to_string(next_date)
        return next_date

    def _create_sale_order(self):
        order_plan_id = self._context.get("order_plan_id")
        available_lines = self.line_ids.filtered(
            lambda line: line.remaining_uom_qty > 0
        )
        if not available_lines:
            return self.env["sale.order"]
        plan = None
        if order_plan_id:
            plan = self.env["blanket.order.plan"].browse(order_plan_id)
            plan._compute_last()
        calculated_before = False
        lines = []
        for line in available_lines:
            if plan and not plan.last:
                plan_qty = line.original_uom_qty * (plan.percent / 100)
                prec = line.product_uom.rounding
                plan_qty = float_round(plan_qty, precision_rounding=prec)
                qty = min(plan_qty, line.remaining_uom_qty)
                calculated_before = True
            else:
                qty = line.remaining_uom_qty
            if qty <= 0:
                continue
            lines.append(
                (
                    0,
                    0,
                    {
                        "blanket_line_id": line.id,
                        "product_id": line.product_id.id,
                        "date_schedule": line.date_schedule,
                        "remaining_uom_qty": line.remaining_uom_qty,
                        "price_unit": line.price_unit,
                        "product_uom": line.product_uom,
                        "qty": qty,
                        "partner_id": line.partner_id,
                    },
                )
            )
        if not lines:
            return self.env["sale.order"]

        wizard = (
            self.env["sale.blanket.order.wizard"]
            .with_context(active_id=self.id, active_model="sale.blanket.order")
            .create({"blanket_order_id": self.id, "line_ids": lines})
        )

        result = wizard.create_sale_order()
        domain = result.get("domain", [])
        if not domain or not domain[0]:
            return self.env["sale.order"]
        sale_order_id = domain[0][2][0]
        orders = self.env["sale.order"].search([("id", "=", sale_order_id)])
        if not orders:
            return self.env["sale.order"]
        blanket_orders = self.env["sale.blanket.order"].browse(self.id)
        if plan:
            for order in orders:
                if not calculated_before:
                    plan._compute_new_order_quantity(blanket_orders)
                order.date_order = plan.plan_date
            plan.sale_order_ids += orders
        return orders

    @api.depends("amount_total", "total_service_costs", "total_product_costs")
    def _compute_total_costs(self):
        for order in self:
            order.total_costs = order.total_product_costs + order.total_service_costs

    @api.depends("order_product_ids.amount_total")
    def _compute_total_product_costs(self):
        for order in self:
            order.total_product_costs = sum(
                [line.amount_total for line in order.order_product_ids]
            )

    @api.depends("order_service_ids.amount_total")
    def _compute_total_service_costs(self):
        for order in self:
            order.total_service_costs = sum(
                [line.amount_total for line in order.order_service_ids]
            )

    def action_view_versions(self):
        self.ensure_one()
        version_ids = self.version_ids.mapped("new_blanket_order_id.id")
        if not version_ids:
            return {"type": "ir.actions.act_window_close"}
        return {
            "type": "ir.actions.act_window",
            "name": "Versions",
            "res_model": "sale.blanket.order",
            "view_mode": "tree,form",
            "domain": [("id", "in", version_ids)],
        }

    def action_view_order_plan(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Order Plan",
            "res_model": "blanket.order.plan",
            "view_mode": "tree,form",
            "domain": [("sale_id", "=", self.id)],
        }

    def action_view_product_costs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Product Costs",
            "res_model": "blanket.order.product",
            "view_mode": "tree,form",
            "domain": [("blanket_order_id", "=", self.id)],
        }

    def action_view_service_costs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Service Costs",
            "res_model": "blanket.order.service",
            "view_mode": "tree,form",
            "domain": [("blanket_order_id", "=", self.id)],
        }

    def action_show_account_analytic_line(self):
        self.ensure_one()
        context = dict(self.env.context)
        context.pop("group_by", None)
        context.update({"tree_view_ref": "analytic.view_account_analytic_line_tree"})
        return {
            "type": "ir.actions.act_window",
            "name": _("Account Analytic Line"),
            "res_model": "account.analytic.line",
            "domain": [
                ("account_id", "=", self.analytic_account_id.id),
            ],
            "view_mode": "tree,pivot",
            "context": context,
        }

    def set_to_draft(self):
        for record in self:
            if record.version_ids:
                raise UserError(
                    _(
                        "You cannot set this Blanket Order to Draft because "
                        "it has associated versions."
                    )
                )
        return super().set_to_draft()
