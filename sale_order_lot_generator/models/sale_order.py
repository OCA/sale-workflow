# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_max_lot_index(self):
        self.ensure_one()
        # when a new line is added to confirmed sale order
        # get the max index_lot from the other lines
        index_lot = 0
        lot_ids = self.order_line.filtered(lambda l: l.lot_id).mapped("lot_id")
        for lot in lot_ids:
            lot_name = lot.name
            index_str = lot_name.replace(self.name + "-", "")
            last_index = int(index_str) if index_str.isdigit() else 0
            index_lot = max(index_lot, last_index)
        return index_lot

    def generate_lot(self):
        for rec in self:
            index_lot = rec._get_max_lot_index() + 1
            for line in rec.order_line:
                if (
                    line.product_id.auto_generate_prodlot
                    and not line.lot_id
                    and line.product_id.tracking != "none"
                ):
                    lot_id = line.create_lot(index_lot)
                    index_lot += 1
                    line.lot_id = lot_id

    def action_confirm(self):
        self.generate_lot()
        return super().action_confirm()
