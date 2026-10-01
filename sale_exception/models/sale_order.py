# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from markupsafe import Markup

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = ["sale.order", "base.exception"]
    _name = "sale.order"
    _order = "main_exception_id asc, date_order desc, name desc"

    @api.model
    def _reverse_field(self):
        return "sale_ids"

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
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

    def _check_sale_check_exception(self, vals):
        check_exceptions = any(
            field in vals for field in self._fields_trigger_check_exception()
        )
        if check_exceptions:
            self.sale_check_exception()

    def write(self, vals):
        result = super().write(vals)
        self._check_sale_check_exception(vals)
        return result

    def sale_check_exception(self):
        orders = self.filtered(lambda s: s.state == "sale")
        if orders:
            orders._check_exception()

    def _must_popup_exception(self):
        return self.env.company.sale_exception_show_popup

    def action_confirm(self):
        self.detect_exceptions()
        return super().action_confirm()

    def _validate_order(self):
        # Frontend flows: no rollback, leave blocked orders unconfirmed.
        orders = self.with_context(base_exception_no_rollback={self._name: self.ids})
        orders.detect_exceptions()
        blocked = orders.filtered(lambda o: o._must_raise_exception_after_detection())
        for order in blocked:
            order.message_post(
                body=Markup("{}{}").format(
                    self.env._(
                        "The order was not confirmed because of these exceptions:"
                    ),
                    Markup(order.exceptions_summary or ""),
                ),
                subtype_xmlid="mail.mt_note",
            )
        to_confirm = orders - blocked
        if to_confirm:
            return super(SaleOrder, to_confirm)._validate_order()

    def action_draft(self):
        res = super().action_draft()
        orders = self.filtered("ignore_exception")
        orders.write({"ignore_exception": False})
        return res

    def _sale_get_lines(self):
        self.ensure_one()
        return self.order_line

    @api.model
    def _get_popup_action(self):
        return self.env.ref("sale_exception.action_sale_exception_confirm")
