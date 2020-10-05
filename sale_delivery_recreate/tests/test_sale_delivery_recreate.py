# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleDeliveryRecreate(TransactionCase):

    def _create_sale_order_line(self, order, product, qty):
        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': 100,
            })
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    def setUp(self):
        super(TestSaleDeliveryRecreate, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        # Acoustic Bloc Screens, 16 on hand
        self.product1 = self.env.ref('product.product_product_25')
        # Cabinet with Doors, 8 on hand
        self.product2 = self.env.ref('product.product_product_10')
        # Large Cabinet, 250 on hand
        self.product3 = self.env.ref('product.product_product_6')
        self.product1.invoice_policy = 'order'
        vendor1 = self.env['res.partner'].create(
            {'name': 'AAA', 'email': 'from.test@example.com'})
        supplier_info1 = self.env['product.supplierinfo'].create({
            'name': vendor1.id,
            'price': 50,
        })
        warehouse_1 = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.user.id)], limit=1)
        warehouse_1.write({'delivery_steps': 'pick_pack_ship'})
        warehouse_2 = self.env['stock.warehouse'].create({
            'name': 'Small Warehouse',
            'code': 'SWH'
        })
        warehouse_1.write({
            'resupply_wh_ids': [(6, 0, [warehouse_2.id])]
        })
        resupply_route = self.env['stock.location.route'].search(
            [('supplier_wh_id', '=', warehouse_2.id),
             ('supplied_wh_id', '=', warehouse_1.id)])
        self.assertTrue(resupply_route)
        route_mto = warehouse_1.mto_pull_id.route_id
        self.product2.write({
            'seller_ids': [(6, 0, [supplier_info1.id])],
            'route_ids': [(6, 0, [resupply_route.id, route_mto.id])]
        })

    def test_complete_picking_from_sale(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        self._create_sale_order_line(order, self.product1, 5)
        self._create_sale_order_line(order, self.product2, 10)
        order.action_confirm()
        self.assertEqual(order.state, 'sale')
        pickings_moves_qty = sum(
            order.picking_ids.mapped('move_lines.product_uom_qty'))
        deleted_pickings_moves_qty = sum(
            order.picking_ids[0].mapped('move_lines.product_uom_qty'))
        order.picking_ids[0].action_cancel()
        order.picking_ids[0].unlink()
        self.assertEqual(sum(
            order.picking_ids.mapped('move_lines.product_uom_qty')),
            pickings_moves_qty - deleted_pickings_moves_qty)
        order.delivery_recreate()
        self.assertEqual(sum(
            order.picking_ids.mapped('move_lines.product_uom_qty')),
            pickings_moves_qty)

    def test_partial_picking_from_sale(self):
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        self._create_sale_order_line(order1, self.product1, 5)
        self._create_sale_order_line(order1, self.product2, 10)
        order1.action_confirm()
        self.assertEqual(order1.state, 'sale')
        out_pickings = order1.picking_ids.filtered(
            lambda x: x.picking_type_code == 'outgoing'
            and x.location_dest_id.usage == 'customer'
        )
        other_pickings = (order1.picking_ids - out_pickings).filtered(
            lambda x: x.state != 'cancel'
        )
        other_pickings_moves_qty = sum(
            other_pickings.mapped('move_lines.product_uom_qty'))
        out_picking = out_pickings[0]
        self.assertEqual(sum(out_pickings.mapped('move_lines.product_uom_qty')), 15)
        out_picking.move_lines[0].quantity_done = 3
        backorder_wiz_id = out_picking.button_validate()['res_id']
        backorder_wiz = self.env['stock.backorder.confirmation'].browse(
            backorder_wiz_id)
        backorder_wiz.process()
        out_pickings = order1.picking_ids.filtered(
            lambda x: x.picking_type_code == 'outgoing'
            and x.location_dest_id.usage == 'customer'
        )
        # delete the second out picking
        picking1 = out_pickings - out_picking
        picking1.action_cancel()
        picking1.unlink()
        order1.delivery_recreate()
        out_pickings = order1.picking_ids.filtered(
            lambda x: x.picking_type_code == 'outgoing'
            and x.location_dest_id.usage == 'customer'
        )
        self.assertEqual(
            sum(out_pickings.mapped('move_lines.product_uom_qty')), 15)
        other_pickings = (order1.picking_ids - out_pickings).filtered(
            lambda x: x.state != 'cancel'
        )
        self.assertEqual(other_pickings_moves_qty, sum(
            other_pickings.mapped('move_lines.product_uom_qty')))
