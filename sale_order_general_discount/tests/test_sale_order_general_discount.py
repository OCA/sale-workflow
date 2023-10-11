# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.tests import SavepointCase


class TestSaleOrderGeneralDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test", "sale_discount": 10.0}
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "Contact Test",
                "parent_id": cls.partner.id,
                "type": "contact",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        cls.product_consu = cls.env["product.product"].create(
            {"name": "test_product_consu", "type": "consu"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )
        cls.contact_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.contact.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

    def test_default_partner_discount(self):
        self.assertEqual(self.order.general_discount, self.partner.sale_discount)

    def test_contact_partner_discount(self):
        self.assertEqual(
            self.contact_order.general_discount, self.partner.sale_discount
        )

    def test_sale_order_values(self):
        self.order.general_discount = 10
        self.assertEqual(self.order.order_line.price_subtotal, 900.00)

    def _get_ctx_from_view(self, res):
        order_xml = etree.XML(res["arch"])
        order_line_path = "//field[@name='order_line']"
        order_line_field = order_xml.xpath(order_line_path)[0]
        return order_line_field.attrib.get("context", "{}")

    def test_general_discount_product_filter(self):
        """With the filter, the first line should not be discounted
        rate, while the second follows the general discount
        """
        self.order.company_id.general_discount_applicable_to = (
            '[("type", "=", "consu")]'
        )
        self.order.order_line = [
            (
                0,
                0,
                {
                    "sequence": 100,
                    "name": self.product_consu.name,
                    "product_id": self.product_consu.id,
                    "product_uom_qty": 1,
                    "product_uom": self.product_consu.uom_id.id,
                    "price_unit": 1000.00,
                },
            )
        ]

        self.order.general_discount = 30

        self.assertEqual(self.order.order_line[0].price_subtotal, 1000.00)
        self.assertEqual(self.order.order_line[1].price_subtotal, 700.00)
