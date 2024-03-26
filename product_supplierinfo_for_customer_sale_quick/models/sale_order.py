from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_context_add_products(self):
        res = super()._get_context_add_products()
        res.update(
            {
                "partner_id": self.partner_id.id,
            }
        )
        return res
