# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase
from odoo.exceptions import ValidationError


class TestProductSerialUnique(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "lang": "en_US"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "type": "product",
                "tracking": "serial",
                "invoice_policy": "delivery",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product Test 2",
                "type": "product",
                "tracking": "serial",
                "invoice_policy": "delivery",
            }
        )

        cls.lot1 = cls.env["stock.production.lot"].create(
            {"name": "Serial 1", "product_id": cls.product.id}
        )
        cls.lot2 = cls.env["stock.production.lot"].create(
            {"name": "Serial 2", "product_id": cls.product.id}
        )
        cls.serial = cls.env["stock.production.lot"].create(
            {"name": "Serial 1", "product_id": cls.product2.id}
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 15.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product2.name,
                            "product_id": cls.product2.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product2.uom_id.id,
                            "price_unit": 10.0,
                        },
                    ),
                ],
            }
        )

    def test_change_qty(self):
        with self.assertRaises(ValidationError):
            self.sale.order_line[0].product_uom_qty = 2.0
