# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleStockPartnerVersion(TransactionCase):

    def setUp(self):
        super(TestSaleStockPartnerVersion, self).setUp()
        self.sale = self.env.ref('sale.sale_order_1')
        partner_vals = {
            'name': u'Name',
            'street': u'Street',
            'street2': u'Street2',
            'zip': u'Zip',
            'city': u'City',
            'country_id': self.env.ref('base.fr').id}
        self.partner = self.env['res.partner'].create(partner_vals)

    def test_sale_version_stock_picking(self):
        self.sale.partner_shipping_id = self.partner
        self.sale.action_confirm()
        picking = self.sale.picking_ids[0]
        self.assertTrue(picking.partner_id, self.partner)
        self.partner.write({'city': 'new city'})
        self.sale.invalidate_cache()
        self.assertNotEqual(self.sale.partner_shipping_id, self.partner)
        self.assertEqual(self.sale.partner_shipping_id.parent_id, self.partner)
        self.assertEqual(picking.partner_id, self.sale.partner_shipping_id)
