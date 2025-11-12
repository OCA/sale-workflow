# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests import TransactionCase


class TestSalePartnerShippingDefaultPartnerInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.shipping_partner = cls.env["res.partner"].create(
            {"name": "Test Shipping Partner"}
        )
        cls.invoice_partner = cls.env["res.partner"].create(
            {"name": "Test Invoice Partner"}
        )

    def create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.shipping_partner.id,
            }
        )

    def test_sale_order_partner_invoice(self):
        sale_order = self.create_sale_order()
        self.assertNotEqual(sale_order.partner_invoice_id, self.invoice_partner)
        self.shipping_partner.default_partner_invoice_id = self.invoice_partner
        sale_order = self.create_sale_order()
        self.assertEqual(sale_order.partner_invoice_id, self.invoice_partner)
