# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.tests import TransactionCase


class TestSaleOrderLineInput(TransactionCase):
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
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Public Pricelist", "sequence": 1}
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product without general discount",
                "type": "service",
                "general_discount_apply": False,
            }
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
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product2.name,
                            "product_id": cls.product2.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product2.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    ),
                ],
                "pricelist_id": cls.pricelist.id,
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
                "pricelist_id": cls.pricelist.id,
            }
        )
        cls.View = cls.env["ir.ui.view"]

    def test_default_partner_discount(self):
        self.assertEqual(self.order.general_discount, self.partner.sale_discount)

    def test_contact_partner_discount(self):
        self.assertEqual(
            self.contact_order.general_discount, self.partner.sale_discount
        )

    def test_sale_order_values(self):
        self.order.general_discount = 10
        self.assertEqual(self.order.order_line[0].price_subtotal, 900.00)
        self.assertEqual(self.order.order_line[1].price_subtotal, 1000.00)

    def _get_ctx_from_view(self, res):
        order_xml = etree.XML(res["arch"])
        order_line_path = "//field[@name='order_line']"
        order_line_field = order_xml.xpath(order_line_path)[0]
        return order_line_field.attrib.get("context", "{}")

    def test_default_line_discount_value(self):
        res = self.order.get_view(
            view_id=self.env.ref(
                "sale_order_general_discount." "sale_order_general_discount_form_view"
            ).id,
            view_type="form",
        )
        ctx = self._get_ctx_from_view(res)
        self.assertTrue("default_discount" in ctx)
        view = self.View.create(
            {
                "name": "test",
                "type": "form",
                "model": "sale.order",
                "arch": """
                <form>
                    <field name='order_line'
                        context="{'default_product_uom_qty': 3.0}">
                    </field>
                </form>
            """,
            }
        )
        res = self.order.get_view(view_id=view.id, view_type="form")
        ctx = self._get_ctx_from_view(res)
        self.assertTrue("default_discount" in ctx)

    def test_sale_order_line_wo_form_view(self):
        self.order.general_discount = 10
        vals = {
            "name": self.product.name,
            "product_id": self.product.id,
            "product_uom_qty": 1,
            "product_uom": self.product.uom_id.id,
            "price_unit": 1000.00,
            "order_id": self.order.id,
        }
        order_line = self.env["sale.order.line"].create(vals)
        self.assertEqual(order_line.price_subtotal, 900.00)
        self.assertEqual(order_line.discount, 10)
        vals["discount"] = 20
        order_line2 = self.env["sale.order.line"].create(vals)
        self.assertEqual(order_line2.price_subtotal, 800.00)
        self.assertEqual(order_line2.discount, 20)

    def test_compute_discount(self):
        self.order.general_discount = 10
        self.assertEqual(self.order.order_line[0].discount, 10)
        self.assertEqual(self.order.order_line[1].discount, 0)
        self.order.order_line[0].discount = 1
        self.order.order_line[1].discount = 2
        self.order.order_line._compute_discount()
        self.assertEqual(self.order.order_line[0].discount, 10)
        self.assertEqual(self.order.order_line[1].discount, 0)

    def test_product_template(self):
        self.assertTrue(self.product.product_tmpl_id.general_discount_apply)
        self.assertFalse(self.product2.product_tmpl_id.general_discount_apply)
        self.product2.product_tmpl_id.general_discount_apply = True
        self.assertTrue(self.product2.general_discount_apply)

    def test_search_product_template_per_general_discount_apply(self):
        self.assertEqual(
            self.env["product.template"]
            .search([("general_discount_apply", "=", 0)])
            .id,
            self.product2.product_tmpl_id.id,
        )
