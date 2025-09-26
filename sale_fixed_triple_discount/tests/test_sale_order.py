# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import TransactionCase
from odoo.tests.common import Form


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("product.group_discount_per_so_line")
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env.ref("product.product_product_3")

    def _create_sale(self, **kwargs):
        sale_vals = [
            Command.create(
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "name": "Line 1",
                    "price_unit": 200.00,
                    **kwargs,
                },
            )
        ]
        return self.env["sale.order"].create(
            {"partner_id": self.partner.id, "order_line": sale_vals}
        )

    def test_01_show_discount_warning_label(self):
        sale = self._create_sale(discount_fixed=10.00, discount1=10.00)
        self.assertTrue(sale.show_discount_warning_label)
        with Form(sale) as sale_form:
            with sale_form.order_line.edit(0) as line:
                line.discount_fixed = 0.0
        self.assertFalse(sale.show_discount_warning_label)

    def test_02_get_lines_to_compute_discount(self):
        sale = self._create_sale(discount1=10.00, discount2=10.00)
        self.assertAlmostEqual(sale.order_line[0].discount, 19)
        lines = sale.order_line._get_lines_to_compute_discount()
        self.assertEqual(lines, sale.order_line)
        with Form(sale) as sale_form:
            with sale_form.order_line.edit(0) as line:
                line.discount_fixed = 10.0
        lines = sale.order_line._get_lines_to_compute_discount()
        self.assertEqual(lines, sale.order_line - sale.order_line[0])

    def test_03_should_copy_discount_to_discount1(self):
        sale = self._create_sale(discount=10.00)
        self.assertAlmostEqual(sale.order_line[0].discount1, 10)
        self.assertAlmostEqual(sale.order_line[0].discount, 10)
        sale_2 = self._create_sale(discount=10.00, discount_fixed=10.00)
        self.assertAlmostEqual(sale_2.order_line[0].discount1, 10)
        self.assertAlmostEqual(sale_2.order_line[0].discount_fixed, 10)
