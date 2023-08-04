# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_open_sale_order_change_analytic_wizard(self):
        return {
            "name": _("Update Analytic Account"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order.change.analytic",
            "view_mode": "form",
            "context": self.env.context,
            "target": "new",
        }
