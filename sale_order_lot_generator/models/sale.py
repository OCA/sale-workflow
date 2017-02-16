# coding: utf-8
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_vals_lot_number(self, order_line, index_lot):
        """Prepare values before creating a lot number"""
        lot_number = "%s-%03d" % (order_line.order_id.name, index_lot)
        return {
            'name': lot_number,
            'product_id': order_line.product_id.id,
        }

    @api.multi
    def generate_prodlot(self):
        lot_m = self.env['stock.production.lot']
        for rec in self:
            index_lot = 1
            for line in rec.order_line:
                line_vals = {}
                if (line.product_id.auto_generate_prodlot and
                    not line.lot_id and
                        line.product_id.tracking != 'none'):
                    vals = rec._prepare_vals_lot_number(line, index_lot)
                    index_lot += 1
                    lot_id = lot_m.create(vals)
                    line_vals['lot_id'] = lot_id.id
                    line.write(line_vals)

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.generate_prodlot()
        return super(SaleOrder, self).action_confirm()

    @api.model
    def _check_move_state(self, line):
        if not line.product_id.auto_generate_prodlot:
            return super(SaleOrder, self)._check_move_state(line)
        else:
            return True

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for sale in self:
            for line in sale.order_line:
                line.lot_id.unlink()
        return res
