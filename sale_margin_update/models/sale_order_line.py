# Copyright 2024 SDi Sidoo Soluciones S.L. <www.sidoo.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def wizard_price_unit_by_margin(self):
        return {
            "name": _("Update Sale Order Line Price by Margin"),
            "type": "ir.actions.act_window",
            "res_model": "sale.recalculate.price.margin",
            "view_mode": "form",
            "target": "new",
            "context": dict(self.env.context, default_line_id=self.id),
        }
