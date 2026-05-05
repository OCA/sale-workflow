# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form, TransactionCase


class TestSaleOrderLinePackagingRequired(TransactionCase):
    """Test packaging required on sale order lines."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product_with_packaging = cls.env["product.product"].create(
            {
                "name": "Product With Packaging",
                "type": "consu",
                "list_price": 100.0,
            }
        )
        cls.product_without_packaging = cls.env["product.product"].create(
            {
                "name": "Product Without Packaging",
                "type": "consu",
                "list_price": 50.0,
            }
        )
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "Test Packaging",
                "product_id": cls.product_with_packaging.id,
                "qty": 10.0,
            }
        )

    def test_has_packaging_available(self):
        """Check product_packaging_id is required when product has packaging."""
        with Form(self.env["sale.order"]) as sale_form:
            sale_form.partner_id = self.partner
            with self.assertRaisesRegex(AssertionError, "product_packaging_id"):
                with sale_form.order_line.new() as line:
                    line.product_id = self.product_with_packaging
                    self.assertTrue(line.has_packaging_available)

    def test_has_not_packaging_available(self):
        """Check has_packaging_available is False when product has no packaging."""
        with Form(self.env["sale.order"]) as sale_form:
            sale_form.partner_id = self.partner
            with sale_form.order_line.new() as line:
                line.product_id = self.product_without_packaging
                self.assertFalse(line.has_packaging_available)
            sale_form.save()
