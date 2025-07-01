from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        picking_values = super()._get_new_picking_values()
        if self.group_id.sale_id.priority:
            picking_values["priority"] = self.group_id.sale_id.priority
        return picking_values
