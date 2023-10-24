# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.tests import TransactionCase


class TestSaleOrderLineInput(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
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
        cls.View = cls.env["ir.ui.view"]

    def test_default_partner_discount(self):
        self.assertEqual(self.order.general_discount, self.partner.sale_discount)

    def test_contact_partner_discount(self):
        self.assertEqual(
            self.contact_order.general_discount, self.partner.sale_discount
        )

    def test_sale_order_values(self):
        self.order.general_discount = 10
        self.assertEqual(self.order.order_line.price_reduce, 900.00)

    def _get_ctx_from_view(self, res):
        order_xml = etree.XML(res["arch"])
        order_line_path = "//field[@name='order_line']"
        order_line_field = order_xml.xpath(order_line_path)[0]
        return order_line_field.attrib.get("context", "{}")

    def test_default_line_discount_value(self):

        res = self.order.fields_view_get(
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
                <data>
                    <field name='order_line'
                        context="{'default_product_uom_qty': 3.0}">
                    </field>
                </data>
            """,
            }
        )
        res = self.order.fields_view_get(view_id=view.id, view_type="form")
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
