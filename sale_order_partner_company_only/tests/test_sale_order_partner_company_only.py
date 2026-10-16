# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from lxml import etree

from odoo.tests.common import TransactionCase


class TestPartnerCompanyOnly(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a company partner
        cls.company_partner = cls.env["res.partner"].create(
            {
                "name": "Test Company",
                "is_company": True,
            }
        )

        # Create an individual contact (not a company)
        cls.individual_contact = cls.env["res.partner"].create(
            {
                "name": "Test Individual",
                "is_company": False,
            }
        )

        # Create a product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
            }
        )

    def test_01_partner_domain_in_view(self):
        """Test that partner_id field has company-only domain in the view."""
        sale_order = self.env["sale.order"]
        view = self.env.ref("sale.view_order_form")

        # Get the view arch with our module's modifications
        view_info = sale_order.get_view(view_id=view.id)
        doc = etree.fromstring(view_info["arch"])  # Find partner_id field in the view
        partner_fields = doc.xpath("//field[@name='partner_id']")

        # Check that at least one partner_id field has the company domain
        domain_found = False
        field = partner_fields[0]
        domain = field.get("domain")
        if "('is_company', '=', True)" in domain:
            domain_found = True

        self.assertTrue(
            domain_found,
            "partner_id field should have a domain restricting to companies",
        )

    def test_02_sale_order_with_company(self):
        """Test creating a sale order with a company partner works."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.company_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        self.assertEqual(sale_order.partner_id, self.company_partner)

    def test_03_individual_contact_excluded_by_domain(self):
        """Test that individual contacts are excluded by the view domain.

        The domain restricts partner_id to companies only. A contact with
        is_company=False must not appear in a search using that domain.
        """
        domain = [("is_company", "=", True)]
        results = self.env["res.partner"].search(domain)
        self.assertIn(
            self.company_partner,
            results,
            "Company partner should be included in restricted domain search",
        )
        self.assertNotIn(
            self.individual_contact,
            results,
            "Individual contact should be excluded by the is_company domain",
        )
