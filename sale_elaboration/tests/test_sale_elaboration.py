# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestSaleElaboration(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Elaboration = cls.env['product.elaboration']
        cls.product = cls.env['product.product'].create({
            'name': 'test',
        })
        cls.product_elaboration_A = cls.env['product.product'].create({
            'name': 'Product Elaboration A',
            'type': 'service',
            'list_price': 50.0,
        })
        cls.product_elaboration_B = cls.env['product.product'].create({
            'name': 'Product Elaboration B',
            'type': 'service',
            'list_price': 25.0,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'test - partner',
        })
        cls.elaboration_a = cls.Elaboration.create({
            'code': 'AA',
            'name': 'Elaboration A',
            'product_id': cls.product_elaboration_A.id,
        })
        cls.elaboration_b = cls.Elaboration.create({
            'code': 'BB',
            'name': 'Elaboration B',
            'product_id': cls.product_elaboration_B.id,
        })
        so = cls.env['sale.order'].new({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_uom_qty': 10.0,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 1000.00,
                'elaboration_id': cls.elaboration_a.id,
                'elaboration_note': 'elaboration A',
            })],
        })
        so.onchange_partner_id()
        cls.order = cls.env['sale.order'].create(
            so._convert_to_write(so._cache))

    def test_search_elaboration(self):
        elaboration = self.Elaboration.name_search('Elaboration')
        self.assertEqual(len(elaboration), 2)
        elaboration = self.Elaboration.name_search('AA')
        self.assertEqual(len(elaboration), 1)

    def test_sale_elaboration_change(self):
        self.order.order_line.elaboration_id = self.elaboration_b.id
        self.order.order_line.onchange_elaboration_id()
        self.assertEqual(
            self.order.order_line.elaboration_note, 'Elaboration B')

    def test_sale_elaboration(self):
        self.order.action_confirm()
        self.order.picking_ids.move_lines.quantity_done = 10.0
        self.order.picking_ids.action_done()
        elaboration_lines = self.order.order_line.filtered('is_elaboration')
        self.assertEqual(len(elaboration_lines), 1)
        self.assertEqual(elaboration_lines.price_unit, 50.0)

    def test_sale_elaboration_multi(self):
        self.order.order_line.create({
            'order_id': self.order.id,
            'product_id': self.product_elaboration_A.id,
            'product_uom_qty': 1.0,
            'price_unit': 50.0,
            'is_elaboration': True,
        })
        self.order.action_confirm()
        self.order.picking_ids.move_lines.quantity_done = 10.0
        self.order.picking_ids.action_done()
        elaboration_lines = self.order.order_line.filtered('is_elaboration')
        self.assertEqual(len(elaboration_lines), 1)
        self.assertEqual(elaboration_lines.product_uom_qty, 11.0)
