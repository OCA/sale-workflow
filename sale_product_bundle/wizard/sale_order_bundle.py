# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import fields, api, _

import openerp.addons.decimal_precision as dp


class SaleOrderBundle(osv.osv_memory):
    _name = 'sale.order.bundle'
    _rec_name = 'product_bundle_id'

    product_bundle_id = fields.Many2one(
        'product.bundle', _('Product bundle'), required=True)
    quantity = fields.Float(
        string=_('Quantity'),
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        default=1)

    @api.multi
    def add_bundle(self):
        """ Add product bundle, multiplied by quantity in sale order line """
        so_id = self._context['active_id']
        if not so_id:
            return
        sale_order_line = self.env['sale.order.line']
        for bundle_line in self.product_bundle_id.bundle_line_ids:
            sale_order_line.create(
                self.prepare_sale_order_line_data(so_id, self.product_bundle_id,
                                                  bundle_line))

    def prepare_sale_order_line_data(self, sale_order_id, bundle, bundle_line):
        return {
            'order_id': sale_order_id,
            'product_id': bundle_line.product_id.id,
            'product_uom_qty': bundle_line.quantity * self.quantity,
        }
