# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class sale_order(models.Model):
    _inherit = 'sale.order'

    # Copia del modulo de pxgeo
    def create(self, cr, uid, vals, context=None):
        result = super(sale_order, self).create(cr, uid, vals, context)
        self.expand_packs(cr, uid, [result], context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        result = super(sale_order, self).write(cr, uid, ids, vals, context)
        if 'order_line' in vals:
            self.expand_packs(cr, uid, ids, context)
        return result

    def copy(self, cr, uid, id, default={}, context=None):
        line_obj = self.pool.get('sale.order.line')
        result = super(sale_order, self).copy(cr, uid, id, default, context)
        sale = self.browse(cr, uid, result, context)
        for line in sale.order_line:
            if line.pack_parent_line_id:
                line_obj.unlink(cr, uid, [line.id], context)
        self.expand_packs(cr, uid, sale.id, context)
        return result

    def expand_packs(self, cr, uid, ids, context={}, depth=1):
        if type(ids) in [int, long]:
            ids = [ids]
        if depth == 10:
            return
        updated_orders = []
        for order in self.browse(cr, uid, ids, context):

            fiscal_position = (
                order.fiscal_position
                and self.pool.get('account.fiscal.position').browse(
                    cr, uid, order.fiscal_position.id, context
                )
                or False
            )
            """
            The reorder variable is used to ensure lines of the same pack go
            right after their parent. What the algorithm does is check if the
            previous item had children. As children items must go right after
            the parent if the line we're evaluating doesn't have a parent it
            means it's a new item (and probably has the default 10 sequence
            number - unless the appropiate c2c_sale_sequence module is
            installed). In this case we mark the item for reordering and
            evaluate the next one. Note that as the item is not evaluated and
            it might have to be expanded it's put on the queue for another
            iteration (it's simple and works well). Once the next item has been
            evaluated the sequence of the item marked for reordering is updated
            with the next value.
            """
            sequence = -1
            reorder = []
            last_had_children = False
            lines_to_unlink = []
            for line in order.order_line:
                if last_had_children and not line.pack_parent_line_id:
                    reorder.append(line.id)
                    if (
                        line.product_id.pack_line_ids
                        and order.id not in updated_orders
                    ):
                        updated_orders.append(order.id)
                    continue

                sequence += 1

                if sequence > line.sequence:
                    self.pool.get('sale.order.line').write(
                        cr, uid, [line.id], {'sequence': sequence, }, context)
                else:
                    sequence = line.sequence

                if line.state != 'draft':
                    continue
                if not line.product_id or not line.product_id.pack or line.product_id.sale_order_pack:
                    continue

                """ If pack was already expanded (in another create/write
                operation or in a previous iteration) don't do it again. """
                if line.pack_child_line_ids:
                    # Cambiamos esto para que se borren las lienas viejas y se
                    # creen nuevas
                    unlink_line_ids = [x.id for x in line.pack_child_line_ids]
                    lines_to_unlink.extend(unlink_line_ids)
                    # last_had_children = True
                    # continue
                last_had_children = False
                # pack_price = 0.0

                for subline in line.product_id.pack_line_ids:
                    vals = subline.get_sale_order_line_vals(
                        line, order, sequence, fiscal_position)
                    # sequence += 1

                    # subproduct = subline.product_id
                    # quantity = subline.quantity * line.product_uom_qty

                    # tax_ids = self.pool.get('account.fiscal.position').map_tax(
                    #     cr, uid, fiscal_position, subproduct.taxes_id)
                    # tax_id = [(6, 0, tax_ids)]

                    # if subproduct.uos_id:
                    #     uos_id = subproduct.uos_id.id
                    #     uos_qty = quantity * subproduct.uos_coeff
                    # else:
                    #     uos_id = False
                    #     uos_qty = quantity

                    # if line.product_id.pack_price_type == 'fixed_price':
                    #     price = 0.0
                    #     discount = 0.0
                    # elif line.product_id.pack_price_type == 'totalice_price':
                    #     pack_price += (price * uos_qty)
                    #     price = 0.0
                    #     discount = 0.0
                    #     tax_id = False
                    # else:
                    #     pricelist = order.pricelist_id.id
                    #     price = self.pool.get('product.pricelist').price_get(
                    #         cr, uid, [pricelist], subproduct.id, quantity,
                    #         order.partner_id.id, {
                    #             'uom': subproduct.uom_id.id,
                    #             'date': order.date_order,
                    #             }
                    #         )[pricelist]
                    #     discount = line.discount

                    # Obtain product name in partner's language
                    # ctx = {'lang': order.partner_id.lang}
                    # subproduct_name = self.pool.get('product.product').browse(
                    #     cr, uid, subproduct.id, ctx).name

                    # vals = {
                    #     'order_id': order.id,
                    #     'name': '%s%s' % (
                    #         '> ' * (line.pack_depth+1), subproduct_name
                    #     ),
                    #     'sequence': sequence,
                    # 'delay': subproduct.sale_delay or 0.0,
                    #     'product_id': subproduct.id,
                    # 'procurement_ids': (
                    # [(4, x.id) for x in line.procurement_ids]
                    # ),
                    #     'price_unit': price,
                    #     'tax_id': tax_id,
                    #     'address_allotment_id': False,
                    #     'product_uom_qty': quantity,
                    #     'product_uom': subproduct.uom_id.id,
                    #     'product_uos_qty': uos_qty,
                    #     'product_uos': uos_id,
                    #     'product_packaging': False,
                    #     'discount': discount,
                    #     'number_packages': False,
                    #     'th_weight': False,
                    #     'state': 'draft',
                    #     'pack_parent_line_id': line.id,
                    #     'pack_depth': line.pack_depth + 1,
                    # }

                    self.pool.get('sale.order.line').create(
                        cr, uid, vals, context)
                    if order.id not in updated_orders:
                        updated_orders.append(order.id)

                for id in reorder:
                    sequence += 1
                    self.pool.get('sale.order.line').write(
                        cr, uid, [id], {'sequence': sequence, }, context)

        # Borramos las lienas que se actualizan
        self.pool.get('sale.order.line').unlink(
            cr, uid, lines_to_unlink, context=context)

        return

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
