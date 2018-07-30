# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestSaleOrderLineInput(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test',
            'sale_discount': 10.0,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'test_product',
            'type': 'service',
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_uom_qty': 1,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 1000.00,
            })],
            'pricelist_id': cls.env.ref('product.list0').id,
        })

    def test_default_partner_discount(self):
        self.order.onchange_partner_id()
        self.assertEqual(self.order.discount, self.partner.sale_discount)

    def test_sale_order_values(self):
        self.order.discount = 10
        self.assertEqual(self.order.amount_discount, 100.00)
        self.assertEqual(self.order.order_line.amount_order_discount, 100.00)
        self.assertEqual(self.order.order_line.price_reduce, 900.00)

    def test_prepare_invoice(self):
        self.order.discount = 10
        invoice_vals = self.order.order_line._prepare_invoice_line(1.0)
        self.assertEqual(invoice_vals['discount'], 10)
        self.order.order_line.discount = 20
        invoice_vals = self.order.order_line._prepare_invoice_line(1.0)
        self.assertEqual(invoice_vals['discount'], 28.0)
