from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("general_discount")
    def onchange_general_discount(self):
        for line in self.order_line:
            line._compute_discount()
