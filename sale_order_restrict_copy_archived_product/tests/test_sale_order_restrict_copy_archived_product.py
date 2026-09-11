# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestSaleOrderRestrictCopyArchivedProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create({"name": "Product"})
        cls.product_archived = cls.env["product.product"].create(
            {
                "name": "Product Archived",
                "active": False,
            }
        )

    def test_restriction(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_archived.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        with self.assertRaises(exceptions.ValidationError):
            sale.copy()

    def test_no_restriction(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
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
        sale2 = sale.copy()
        self.assertTrue(sale2)
