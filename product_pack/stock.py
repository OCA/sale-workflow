# -*- encoding: latin-1 -*-


import math
from openerp.osv import fields,osv

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'pack_depth': fields.integer('Depth', required=True, help='Depth of the product if it is part of a pack.'),
        'pack_parent_line_id': fields.many2one('stock.move', 'Pack', help='The pack that contains this product.'),
        'pack_child_line_ids': fields.one2many('stock.move', 'pack_parent_line_id', 'Lines in pack', help=''),
    }
    _defaults = {
        'pack_depth': lambda *a: 0,
    }

stock_move()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'


    def create(self, cr, uid, vals, context=None):
        result = super(stock_picking,self).create(cr, uid, vals, context)
        self.expand_packs(cr, uid, [result], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(stock_picking,self).write(cr, uid, ids, vals, context)
        self.expand_packs(cr, uid, ids, context)
        return result

    def expand_packs(self, cr, uid, ids, context={}, depth=1):
        if depth == 10:
            return
        updated_orders = []
        for order in self.browse(cr, uid, ids, context):
            

            # The reorder variable is used to ensure lines of the same pack go right after their 
            # parent.
            # What the algorithm does is check if the previous item had children. As children items 
            # must go right after the parent if the line we're evaluating doesn't have a parent it
            # means it's a new item (and probably has the default 10 sequence number - unless the 
            # appropiate c2c_sale_sequence module is installed). In this case we mark the item for
            # reordering and evaluate the next one. Note that as the item is not evaluated and it might
            # have to be expanded it's put on the queue for another iteration (it's simple and works well).
            # Once the next item has been evaluated the sequence of the item marked for reordering is updated
            # with the next value.
            # sequence = -1
            reorder = []
            last_had_children = False
            for line in order.move_lines:
                if last_had_children and not line.pack_parent_line_id:
                    reorder.append( line.id )
                    if line.product_id.pack_line_ids and not order.id in updated_orders:
                        updated_orders.append( order.id )
                    continue

                if line.sale_line_id or line.sale_line_id:
                    continue
                if line.state != 'draft':
                    continue
                if not line.product_id:
                    continue
                # If pack was already expanded (in another create/write operation or in 
                # a previous iteration) don't do it again.
                if line.pack_child_line_ids:
                    last_had_children = True
                    continue
                last_had_children = False

                for subline in line.product_id.pack_line_ids:

                    subproduct = subline.product_id
                    # quantity = subline.quantity * line.product_uom_qty
                    quantity = subline.quantity * line.product_qty

                    # if line.product_id.pack_fixed_price:
                    #     # price = 0.0
                    #     # discount = 0.0
                    # else:
                    #     # pricelist = order.pricelist_id.id
                    #     price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], 
                    #                     subproduct.id, quantity, order.partner_id.id, {
                    #         'uom': subproduct.uom_id.id,
                    #         'date': order.date_order,
                    #     })[pricelist]
                    #     discount = line.discount

                    # Obtain product name in partner's language
                    ctx = {'lang': order.partner_id.lang}
                    subproduct_name = self.pool.get('product.product').browse(cr, uid, subproduct.id, ctx).name

                    # tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_position, subproduct.taxes_id)

                    if subproduct.uos_id:
                        uos_id = subproduct.uos_id.id
                        uos_qty = quantity * subproduct.uos_coeff
                    else:
                        uos_id = False
                        uos_qty = quantity

                    vals = {
                        'name': line.picking_id.origin or '' + ':' + subproduct.name,
                        'product_id': subproduct.id,
                        'product_qty': quantity,
                        'product_uos_qty': quantity,
                        'product_uom': subproduct.uom_id.id,
                        'location_id': line.location_id.id,
                        'location_dest_id': line.location_dest_id.id,
                        'picking_id': line.picking_id.id,
                        'address_id': line.address_id.id,
                        'date_expected': line.date_expected,
                        'origin': line.origin,
                        'purchase_line_id': line.purchase_line_id.id,
                        'sale_line_id': line.sale_line_id.id,
                        'product_packaging': line.product_packaging,
                        'pack_parent_line_id': line.id,
                        'pack_depth': line.pack_depth + 1,
                    }

                    self.pool.get('stock.move').create(cr, uid, vals, context)
                    if not order.id in updated_orders:
                        updated_orders.append( order.id )

                for id in reorder:
                    self.pool.get('stock.move').write(cr, uid, [id], {}, context)

        if updated_orders:
            # Try to expand again all those orders that had a pack in this iteration.
            # This way we support packs inside other packs.
            self.expand_packs(cr, uid, ids, context, depth+1)
        return

stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
