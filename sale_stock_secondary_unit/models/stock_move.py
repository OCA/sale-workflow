from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        vals["secondary_uom_id"] = self.sale_line_id.secondary_uom_id.id
        vals["secondary_uom_qty"] = self.env.context.get(
            "procure_secondary_uom_qty", {}
        ).get(self.id, self.sale_line_id.secondary_uom_qty)
        return vals
