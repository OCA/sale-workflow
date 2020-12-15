# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    model = fields.Selection(
        selection_add=[
            ("sale.order", "Sale order"),
            ("sale.order.line", "Sale order line"),
        ]
    )
    sale_ids = fields.Many2many("sale.order", string="Sales")


class SaleOrder(models.Model):
    _inherit = ["sale.order", "base.exception"]
    _name = "sale.order"
    _order = "main_exception_id asc, date_order desc, name desc"

    @api.model
    def _reverse_field(self):
        return "sale_ids"

    def detect_exceptions(self):
        all_exceptions = super(SaleOrder, self).detect_exceptions()
        lines = self.mapped("order_line")
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([("state", "=", "draft")])
        order_set.detect_exceptions()
        return True

    def _fields_trigger_check_exception(self):
        return ["ignore_exception", "order_line", "state"]

    @api.model
    def create(self, vals):
        record = super(SaleOrder, self).create(vals)
        check_exceptions = any(
            field in vals for field in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            record.sale_check_exception()
        return record

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        check_exceptions = any(
            field in vals for field in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            self.sale_check_exception()
        return result

    def sale_check_exception(self):
        orders = self.filtered(lambda s: s.state == "sale")
        if orders:
            orders._check_exception()

    @api.onchange("order_line")
    def onchange_ignore_exception(self):
        if self.state == "sale":
            self.ignore_exception = False

    def action_confirm(self):
        if self.detect_exceptions():
            return self._popup_exceptions()
        return super().action_confirm()

    def action_draft(self):
        res = super().action_draft()
        orders = self.filtered(lambda s: s.ignore_exception)
        orders.write({"ignore_exception": False})
        return res

    def _sale_get_lines(self):
        self.ensure_one()
        return self.order_line

    @api.model
    def _get_popup_action(self):
        return self.env.ref("sale_exception.action_sale_exception_confirm")
