from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one("stock.production.lot", "Lot", copy=False)

    @api.onchange("product_id")
    def product_id_change(self):
        super().product_id_change()
        self.lot_id = False

    @api.onchange("product_id")
    def _onchange_product_id_set_lot_domain(self):
        available_lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            location = self.order_id.warehouse_id.lot_stock_id
            quants = self.env["stock.quant"].read_group(
                [
                    ("product_id", "=", self.product_id.id),
                    ("location_id", "child_of", location.id),
                    ("quantity", ">", 0),
                    ("lot_id", "!=", False),
                ],
                ["lot_id"],
                "lot_id",
            )
            available_lot_ids = [quant["lot_id"][0] for quant in quants]
        self.lot_id = False
        return {"domain": {"lot_id": [("id", "in", available_lot_ids)]}}
