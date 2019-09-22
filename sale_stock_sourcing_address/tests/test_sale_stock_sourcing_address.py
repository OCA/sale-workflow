# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests import TransactionCase


class TestStockSourcingAddress(TransactionCase):

    def setUp(self):
        super(TestStockSourcingAddress, self).setUp()
        self.partner_model = self.env['res.partner']
        self.product_model = self.env['product.product']
        self.warehouse_model = self.env['stock.warehouse']

        self.partner = self.partner_model.create({
            'name': 'Test partner'
        })
        self.wh2_partner = self.partner_model.create({
            'name': 'wh2 partner'
        })
        self.product = self.product_model.create({
            'name': 'Test product',
            'type': 'product'
        })
        self.product.product_tmpl_id.invoice_policy = 'order'
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse_2 = self.warehouse_model.create({
            'code': 'WH-T',
            'name': 'Warehouse Test',
            'partner_id': self.wh2_partner.id,
        })

        route_vals = {
            'sale_selectable': True,
            'name': 'ship from other warehouse',
        }
        self.wh2_route = self.env['stock.location.route'].create(route_vals)
        rule_vals = {
            'location_id': self.env.ref(
                'stock.stock_location_customers').id,
            'location_src_id': self.warehouse_2.lot_stock_id.id,
            'action': 'pull',
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'name': 'wh2 rule',
            'route_id': self.wh2_route.id,
            'propagate_warehouse_id': self.warehouse_2.id,
        }
        self.wh2_rule = self.env['stock.rule'].create(rule_vals)

        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'warehouse_id': self.warehouse.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price,
            })],
        })
        self.line = self.so.order_line[0]

    def test_sourcing_address_01(self):
        self.assertEqual(self.line.sourcing_address_id,
                         self.warehouse.partner_id)
        self.line.route_id = self.wh2_route
        self.line.invalidate_cache()
        self.assertEqual(self.line.sourcing_address_id,
                         self.warehouse_2.partner_id)
