# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def generate_prodlot(self):
        for rec in self:
            index_lot = 1
            for line in rec.order_line:
                if (
                    line.product_id.auto_generate_prodlot
                    and not line.lot_id
                    and line.product_id.tracking != "none"
                ):
                    lot_id = line.create_prodlot(index_lot)
                    index_lot += 1
                    line.lot_id = lot_id

    def action_confirm(self):
        self.generate_prodlot()
        return super().action_confirm()

    def action_cancel(self):
        res = super().action_cancel()
        for sale in self:
            for line in sale.order_line:
                line.lot_id.unlink()
        return res
