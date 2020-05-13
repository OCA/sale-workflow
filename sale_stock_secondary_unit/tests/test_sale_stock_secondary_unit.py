# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase, tagged, Form


@tagged('post_install', '-at_install')
class TestSaleStockOrderSecondaryUnit(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.product_uom_kg = cls.env.ref('uom.product_uom_kgm')
        cls.product_uom_gram = cls.env.ref('uom.product_uom_gram')
        cls.product_uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'type': 'product',
            'uom_id': cls.product_uom_kg.id,
            'uom_po_id': cls.product_uom_kg.id,
            'secondary_uom_ids': [
                (0, 0, {
                    'name': 'unit-700',
                    'uom_id': cls.product_uom_unit.id,
                    'factor': 0.7,
                })],
        })
        StockQuant = cls.env['stock.quant']
        StockQuant.create({
            'product_id': cls.product.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'quantity': 2000,
        })
        cls.secondary_unit = cls.env['product.secondary.unit'].search([
            ('product_tmpl_id', '=', cls.product.product_tmpl_id.id),
        ])
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
        cls.partner = cls.env['res.partner'].create({
            'name': 'test - partner',
        })
        order_form = Form(cls.env['sale.order'])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 1
            line_form.price_unit = 1000
        cls.order = order_form.save()

    def test_stock_move_line_secondary_unit(self):
        self.order.order_line.write({
            'secondary_uom_id': self.secondary_unit.id,
            'secondary_uom_qty': 5,
        })
        self.order.order_line.onchange_secondary_uom()
        self.order.action_confirm()
        picking = self.order.picking_ids
        picking.action_assign()
        self.assertEqual(picking.move_line_ids.secondary_uom_qty, 5.0)
