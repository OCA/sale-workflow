# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSalePartnerVersion(TransactionCase):
    def setUp(self):
        super(TestSalePartnerVersion, self).setUp()
        self.sale = self.env.ref("sale.sale_order_1")

    def test_sale_version_partner(self):
        self.assertFalse(self.sale.partner_invoice_id.version_hash)
        self.assertFalse(self.sale.partner_shipping_id.version_hash)
        self.sale.action_confirm()
        self.assertTrue(self.sale.partner_invoice_id.version_hash)
        self.assertTrue(self.sale.partner_shipping_id.version_hash)
