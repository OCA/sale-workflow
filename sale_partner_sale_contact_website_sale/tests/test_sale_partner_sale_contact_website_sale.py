# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestSalePartnerSaleContactWebsiteSale(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.website = cls.env["website"].search([], limit=1)

        cls.partner_company = cls.env["res.partner"].create(
            {
                "name": "Test Company",
                "is_company": True,
            }
        )
        cls.contact_person = cls.env["res.partner"].create(
            {
                "name": "John Doe",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
            }
        )
        cls.delivery_address = cls.env["res.partner"].create(
            {
                "name": "Test Company Warehouse",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "delivery",
            }
        )
        cls.individual = cls.env["res.partner"].create(
            {
                "name": "Standalone Individual",
                "is_company": False,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "type": "consu",
                "website_published": True,
            }
        )

    def _create_order(self, partner, website=True, **extra_vals):
        # Website carts are created in code (Website._create_cart), not
        # through a form view, so no onchange runs on them.  Creating the
        # order with create() reproduces that flow; a Form would trigger the
        # mixin's auto-switch onchange and defeat the purpose of the test.
        vals = {
            "partner_id": partner.id,
            "website_id": self.website.id if website else False,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "product_uom_qty": 1.0,
                        "price_unit": 100.0,
                    },
                )
            ],
        }
        vals.update(extra_vals)
        return self.env["sale.order"].create(vals)

    def test_01_website_order_switches_to_commercial_partner(self):
        """On confirmation, a website order made by a contact person is
        promoted to the commercial partner."""
        order = self._create_order(self.contact_person)
        self.assertEqual(order.partner_id, self.contact_person)

        order.action_confirm()

        self.assertEqual(order.partner_id, self.partner_company)
        self.assertEqual(order.sale_contact_partner_id, self.contact_person)

    def test_02_checkout_addresses_are_preserved(self):
        """The addresses chosen at checkout must not be recomputed from the
        commercial partner when the switch is applied."""
        order = self._create_order(
            self.contact_person,
            partner_invoice_id=self.contact_person.id,
            partner_shipping_id=self.delivery_address.id,
        )
        fiscal_position = order.fiscal_position_id
        payment_term = order.payment_term_id

        order.action_confirm()

        self.assertEqual(order.partner_id, self.partner_company)
        self.assertEqual(order.partner_invoice_id, self.contact_person)
        self.assertEqual(order.partner_shipping_id, self.delivery_address)
        self.assertEqual(order.fiscal_position_id, fiscal_position)
        self.assertEqual(order.payment_term_id, payment_term)

    def test_03_backend_order_not_affected(self):
        """Orders without a website are out of scope: the base module only
        applies the switch through its onchange."""
        order = self._create_order(self.contact_person, website=False)

        order.action_confirm()

        self.assertEqual(order.partner_id, self.contact_person)
        self.assertFalse(order.sale_contact_partner_id)

    def test_04_b2c_website_order_not_switched(self):
        """An individual without a parent company is their own commercial
        partner: nothing to switch."""
        order = self._create_order(self.individual)

        order.action_confirm()

        self.assertEqual(order.partner_id, self.individual)
        self.assertFalse(order.sale_contact_partner_id)

    def test_05_existing_sale_contact_is_kept(self):
        """A sale contact already set on the order takes precedence over the
        partner that placed the order."""
        other_contact = self.env["res.partner"].create(
            {
                "name": "Jane Smith",
                "is_company": False,
                "parent_id": self.partner_company.id,
                "type": "contact",
            }
        )
        order = self._create_order(
            self.contact_person,
            sale_contact_partner_id=other_contact.id,
        )

        order.action_confirm()

        self.assertEqual(order.partner_id, self.partner_company)
        self.assertEqual(order.sale_contact_partner_id, other_contact)
