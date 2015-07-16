# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import fields, api, _

import openerp.addons.decimal_precision as dp


class sale_order_bundle(osv.osv_memory):
    _name = 'sale.order.bundle'
    _rec_name = 'product_bundle_id'

    product_bundle_id = fields.Many2one(
        'product.bundle', _('Product bundle'), required=True)
    quantity = fields.Float(
        string=_('Quantity'), digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)

    @api.multi
    def add_bundle(self):
        """ Add product bundle, multiplied by quantity in sale order line """
        so_id = self._context['active_id']
        if not so_id:
            return
        SaleOrderLine = self.env['sale.order.line']
        for bundle in self.product_bundle_id.bundle_line_ids:
            sol_data = {
                'order_id': so_id,
                'description': bundle.product_id.name,
                'product_id': bundle.product_id.id,
                'price_unit': bundle.product_id.list_price,
                'product_uom_qty': bundle.quantity*self.quantity,
            }
            SaleOrderLine.create(sol_data)
