# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from lxml import html

from odoo import Command
from odoo.tests import TransactionCase


class TestSaleOrderLineProductNameVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Desk Visibility",
                "default_code": False,
                "type": "service",
                "list_price": 100.0,
            }
        )
        cls.description = "Custom desk description"
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "name": cls.description,
                        }
                    ),
                ],
            }
        )
        cls.line = cls.order.order_line.filtered(
            lambda line: line.product_id == cls.product
        )

    def _get_report_description(self):
        report = self.env.ref("sale.action_report_saleorder")
        content, _ = report._render_qweb_html(report.report_name, self.order.ids)
        document = html.fromstring(content)
        return " ".join(document.xpath("//td[@name='td_product_name']//text()"))

    def test_product_name_visibility(self):
        self.assertFalse(self.line.hide_product_name)
        self.assertEqual(self.line.name, self.description)
        report_description = self._get_report_description()
        self.assertIn(self.product.name, report_description)
        self.assertIn(self.description, report_description)
        self.line.hide_product_name = True
        self.assertTrue(self.line.hide_product_name)
        self.assertEqual(self.line.product_id, self.product)
        self.assertEqual(self.line.name, self.description)
        report_description = self._get_report_description()
        self.assertNotIn(self.product.name, report_description)
        self.assertIn(self.description, report_description)
        second_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "name": "Second desk description",
            }
        )
        self.assertTrue(self.line.hide_product_name)
        self.assertFalse(second_line.hide_product_name)
