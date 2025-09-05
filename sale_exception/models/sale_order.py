# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.api import Environment
from odoo.modules.registry import Registry

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

    def action_confirm(self):
        breakpoint()
        with Registry(self.env.cr.dbname).cursor() as new_cr:
            new_env = Environment(new_cr, self.env.uid, self.env.context)
            exception_ids = self.with_env(new_env).detect_exceptions()
            if exception_ids:
                new_cr.commit()
                
        if exception_ids:
            # FIXME: As ValidationError is raised, the client is not refreshed to 
            #  display the exception summary. Should we catch the ValidationError
            #  and use another error class to force that?
            self._check_exception()
        return super().action_confirm()

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
