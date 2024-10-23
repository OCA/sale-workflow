from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def wizard_price_unit_by_margin(self):
        return {
            "name": _("Update Sale Order Line Price by Margin"),
            "type": "ir.actions.act_window",
            "res_model": "recalculate.price.margin",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_id": self.id},
        }
