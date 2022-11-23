from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _include_in_fully_delivered_compute(self):
        self.ensure_one()
        return True
