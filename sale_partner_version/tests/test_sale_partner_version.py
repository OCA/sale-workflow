# -*- coding: utf-8 -*-
# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSalePartnerVersion(TransactionCase):

    def setUp(self):
        super(TestSalePartnerVersion, self).setUp()
        self.sale = self.env.ref('sale.sale_order_1')
        partner_vals = {
            'name': u'Name',
            'street': u'Street',
            'street2': u'Street2',
            'zip': u'Zip',
            'city': u'City',
            'country_id': self.env.ref('base.fr').id}
        self.partner = self.env['res.partner'].create(partner_vals)

    def test_sale_version_partner(self):
        partner = self.sale.partner_invoice_id
        partner.write({'city': 'new city'})
        self.sale.invalidate_cache()
        self.assertEqual(self.sale.partner_invoice_id, partner)
        self.assertNotEqual(self.sale.partner_invoice_id.parent_id, partner)
        self.assertEqual(self.sale.partner_shipping_id, partner)
        self.assertNotEqual(self.sale.partner_shipping_id.parent_id, partner)
        self.sale.action_confirm()
        partner.write({'city': 'city update'})
        self.assertNotEqual(self.sale.partner_invoice_id, partner)
        self.assertEqual(self.sale.partner_invoice_id.parent_id, partner)
        self.assertNotEqual(self.sale.partner_shipping_id, partner)
        self.assertEqual(self.sale.partner_shipping_id.parent_id, partner)

    def test_sale_version_shipping(self):
        self.sale.partner_shipping_id = self.partner
        self.partner.write({'city': 'new city'})
        self.sale.invalidate_cache()
        self.assertEqual(self.sale.partner_shipping_id, self.partner)
        self.assertNotEqual(self.sale.partner_shipping_id.parent_id, self.partner)
        self.sale.action_confirm()
        self.partner.write({'city': 'city update'})
        self.assertNotEqual(self.sale.partner_invoice_id, self.partner)
        self.assertNotEqual(self.sale.partner_shipping_id, self.partner)
        self.assertEqual(self.sale.partner_shipping_id.parent_id, self.partner)

    def test_sale_version_invoice(self):
        self.sale.partner_invoice_id = self.partner
        self.partner.write({'city': 'new city'})
        self.sale.invalidate_cache()
        self.assertEqual(self.sale.partner_invoice_id, self.partner)
        self.assertNotEqual(self.sale.partner_invoice_id.parent_id,
                            self.partner)
        self.sale.action_confirm()
        self.partner.write({'city': 'city update'})
        self.assertNotEqual(self.sale.partner_invoice_id, self.partner)
        self.assertNotEqual(self.sale.partner_shipping_id, self.partner)
        self.assertEqual(self.sale.partner_invoice_id.parent_id, self.partner)

    def test_sale_version_confirmed_invoice(self):
        self.sale.partner_invoice_id = self.partner
        self.sale.action_confirm()
        for line in self.sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        inv_id = self.sale.action_invoice_create()
        self.partner.write({'city': 'new city'})
        self.sale.invalidate_cache()
        self.assertNotEqual(self.sale.partner_invoice_id, self.partner)
        self.assertEqual(self.sale.partner_invoice_id.parent_id, self.partner)
        invoice = self.env['account.invoice'].browse(inv_id)
        self.assertEqual(invoice.partner_id, self.sale.partner_invoice_id)
