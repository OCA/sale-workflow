from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        picking_values = super()._get_new_picking_values()
        if self.reference_ids.sale_ids.priority:
            picking_values["priority"] = self.reference_ids.sale_ids.priority
        return picking_values
