# coding: utf-8
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def generate_prodlot(self):
        for rec in self:
            index_lot = 1
            for line in rec.order_line:
                if (line.product_id.auto_generate_prodlot and
                    not line.lot_id and
                        line.product_id.tracking != 'none'):
                    lot_id = line.create_prodlot(index_lot)
                    index_lot += 1
                    line.lot_id = lot_id

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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _prepare_vals_lot_number(self, index_lot):
        """Prepare values before creating a lot number"""
        lot_number = "%s-%03d" % (self.order_id.name, index_lot)
        return {
            'name': lot_number,
            'product_id': self.product_id.id,
        }

    @api.model
    def create_prodlot(self, index_lot=1):
        lot_m = self.env['stock.production.lot']
        vals = self._prepare_vals_lot_number(index_lot)
        lot_id = lot_m.create(vals)
        return lot_id

    @api.model
    def create(self, values):
        line = self.new(values)
        # we create a lot befor crete a line because the super method
        # must create a procurement and move
        if (line.order_id.state == 'sale' and
            line.product_id.auto_generate_prodlot and
            not line.lot_id and
                line.product_id.tracking != 'none'):
            # wehen a new line is added to confirmed sale order
            # get the max index_lot from the other lines
            index_lot = 0
            lot_ids = line.order_id.order_line.filtered(
                lambda l: l.lot_id).mapped('lot_id')
            for lot in lot_ids:
                lot_name = lot.name
                index_str = lot_name.replace(line.order_id.name + '-', '')
                last_index = int(index_str) if index_str.isdigit() else 0
                index_lot = max(index_lot, last_index)
            index_lot += 1
            lot_id = line.create_prodlot(index_lot)
            values['lot_id'] = lot_id.id
        line = super(SaleOrderLine, self).create(values)
        return line
