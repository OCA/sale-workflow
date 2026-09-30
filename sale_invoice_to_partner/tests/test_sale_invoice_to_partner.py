# Copyright 2026 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleInvoiceToPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.payer = cls.Partner.create({"name": "Payer Co", "is_company": True})
        cls.customer = cls.Partner.create(
            {
                "name": "Customer Co",
                "is_company": True,
                "invoice_to_partner_id": cls.payer.id,
            }
        )
        cls.customer_no_payer = cls.Partner.create(
            {"name": "Plain Customer", "is_company": True}
        )
        cls.child_contact = cls.Partner.create(
            {
                "name": "Ordering Contact",
                "parent_id": cls.customer.id,
                "type": "contact",
            }
        )

    def _new_sale_order(self, partner):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = partner
        return order_form.save()

    def test_invoice_to_partner_used_on_sale_order(self):
        """The customer's Invoice To partner becomes the invoice address."""
        order = self._new_sale_order(self.customer)
        self.assertEqual(order.partner_invoice_id, self.payer)
        # Delivery address is unaffected by the override.
        self.assertEqual(order.partner_shipping_id, self.customer)

    def test_no_invoice_to_keeps_standard_behaviour(self):
        """Without an Invoice To partner the standard address is kept."""
        order = self._new_sale_order(self.customer_no_payer)
        self.assertEqual(order.partner_invoice_id, self.customer_no_payer)

    def test_child_contact_inherits_commercial_partner(self):
        """A contact with no own Invoice To inherits its company's one."""
        order = self._new_sale_order(self.child_contact)
        self.assertEqual(order.partner_invoice_id, self.payer)

    def test_helper_returns_empty_when_unset(self):
        self.assertFalse(self.customer_no_payer._get_invoice_to_partner())
        self.assertEqual(self.child_contact._get_invoice_to_partner(), self.payer)
