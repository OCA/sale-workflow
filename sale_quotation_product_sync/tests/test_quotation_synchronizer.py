# -*- coding: utf-8 -*-
from odoo.tests import common


class TestQuotationSynchronizer(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestQuotationSynchronizer, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.any_customer = cls.env['res.partner'].search([
            ('customer', '=', True),
        ], limit=1)
        cls.template_default = cls.env.ref(
            'website_quote.website_quote_template_default')
        cls.product_2 = cls.env.ref('product.product_product_2')
        cls.product_3 = cls.env.ref('product.product_product_3')
        cls.template_default.write({
            'quote_line': [
                (0, 0, {
                    'product_id': cls.product_3.id,
                    'name': 'Sample Text',
                    'product_uom_qty': 2.,
                    'price_unit': 450.,
                    'product_uom_id': cls.product_3.uom_id.id,
                    'tested_sample': 'Sample3',
                }),
            ],
            'options': [
                (0, 0, {
                    'product_id': cls.product_2.id,
                    'name': cls.product_2.name,
                    'quantity': 1,
                    'price_unit': 38.25,
                    'uom_id': cls.product_2.uom_id.id,
                }),
            ],
        })

    def test_price_propagation(self):
        order = self.env['sale.order'].create({
            'partner_id': self.any_customer.id,
            'template_id': self.template_default.id,
        })
        order.onchange_template_id()
        order_line_p3 = order.order_line.filtered(
            lambda ol: ol.product_id == self.product_3)

        order_copy = order.copy()
        order_copy_line_p3 = order_copy.order_line.filtered(
            lambda ol: ol.product_id == self.product_3)
        order_copy.action_confirm()

        self.assertEqual(order_line_p3.price_unit, 450.0)
        self.assertEqual(order.amount_total, 900.0)
        self.assertEqual(order_copy_line_p3.price_unit, 450.0)
        self.assertEqual(order_copy.amount_total, 900.0)

        self.product_3.list_price = 500
        self.product_2.list_price = 50
        wizard = self.env['sale.quotation.synchronizer'].create({
            'product_ids': [(4, self.product_2.id), (4, self.product_3.id)]
        })
        wizard.execute()
        # The price change should propagate to quotation template line
        self.assertEqual(self.template_default.quote_line.price_unit, 500.0)
        # The price change should propagate to quotation template option
        self.assertEqual(self.template_default.options.price_unit, 50.0)
        # The price change should propagate to 'draft' order
        self.assertEqual(order_line_p3.price_unit, 500.0)
        self.assertEqual(order.amount_total, 1000.0)
        # but not to the confirmed one
        self.assertEqual(order_copy_line_p3.price_unit, 450.0)
        self.assertEqual(order_copy.amount_total, 900.0)
