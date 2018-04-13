# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestMultipleDiscount(common.TransactionCase):

    def setUp(self):
        super(TestMultipleDiscount, self).setUp()

        self.partner = self.env.ref('base.res_partner_1')
        p = self.env.ref('product.service_order_01')
        order_line_dict = {
            'name': p.name,
            'product_id': p.id,
            'product_uom_qty': 2,
            'product_uom': p.uom_id.id,
            'price_unit': p.list_price,
        }

        self.order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, order_line_dict)],
            'pricelist_id': self.env.ref('product.list0').id,
        })

    def test_01_onchange(self):
        self.order.order_line[0].write(
            {'multiple_discount': '+10 + 15,5 -5.5'})
        self.assertEqual(self.order.order_line[0].discount, 19.77)
        self.assertEqual(
            self.order.order_line[0].multiple_discount, '10+15.5-5.5')

        self.order.order_line[0].write({'multiple_discount': None})
        self.assertEqual(self.order.order_line[0].discount, 0.0)

        with self.assertRaises(ValidationError):
            self.order.order_line[0].write(
                {'multiple_discount': '10 + 15,5a'})

    def test_02_create_invoice(self):
        self.order.order_line[0].write(
            {'multiple_discount': '+10 + 15,5 -5.5'})
        self.order.action_confirm()
        invoice_id = self.order.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(
            self.order.order_line[0].discount,
            invoice.invoice_line_ids[0].discount)
        self.assertEqual(
            self.order.order_line[0].multiple_discount,
            invoice.invoice_line_ids[0].multiple_discount)
