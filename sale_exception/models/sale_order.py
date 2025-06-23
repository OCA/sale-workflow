# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    def _register_hook(self):
        # Exceptions must be detected before any other module runs its own
        # `action_confirm` logic. Standard inheritance cannot grant that:
        # modules with no dependency between them are ordered by installation
        # order, so an override that acts before calling `super()` may run
        # first. `sale_loyalty` is one case: it adds the loyalty points before
        # the order is confirmed, so the points were granted even when an
        # exception blocked the confirmation. The same happens with
        # `sale_order_lot_generator`, and it may happen with payment or
        # e-invoicing integrations, whose side effects live outside the
        # transaction and are not undone by a rollback.
        # Patching the resolved `action_confirm` on the registry class puts the
        # detection outermost, whatever the MRO is.
        ModelClass = self.env.registry["sale.order"]

        original_action_confirm = ModelClass.action_confirm

        def patched_action_confirm(self):
            self.detect_exceptions()
            original_func = patched_action_confirm.origin
            return original_func(self)

        patched_action_confirm.origin = original_action_confirm

        ModelClass.action_confirm = patched_action_confirm

        return super()._register_hook()

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
