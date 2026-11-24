# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids += cls.env.ref("sale.group_discount_per_so_line")
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 200.0}
        )

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

    def test_02_fixed_discount_takes_priority(self):
        sale = self._create_sale(discount1=10.00, discount2=10.00)
        line = sale.order_line
        self.assertAlmostEqual(line.discount, 19)
        self.assertAlmostEqual(line.price_subtotal, 162)
        with Form(sale) as sale_form:
            with sale_form.order_line.edit(0) as line_form:
                line_form.discount_fixed = 10.0
        self.assertAlmostEqual(line.discount, 5)
        self.assertAlmostEqual(line.price_subtotal, 190)
        with Form(sale) as sale_form:
            with sale_form.order_line.edit(0) as line_form:
                line_form.discount_fixed = 0.0
        self.assertAlmostEqual(line.discount, 19)

    def test_02b_report_shows_both_discounts(self):
        sale = self._create_sale(discount1=7.5)
        sale |= self._create_sale(discount_fixed=12.34)
        html = str(
            self.env["ir.actions.report"]._render_qweb_html(
                "sale.action_report_saleorder", sale.ids
            )[0]
        )
        # discount1 cell of sale_triple_discount on the product line
        self.assertIn("7.50", html)
        # fixed discount cell of sale_fixed_discount on the product line
        self.assertIn("12.34", html)

    def test_03_should_copy_discount_to_discount1(self):
        sale = self._create_sale(discount=10.00)
        self.assertAlmostEqual(sale.order_line[0].discount1, 10)
        self.assertAlmostEqual(sale.order_line[0].discount, 10)
        sale_2 = self._create_sale(discount=10.00, discount_fixed=10.00)
        self.assertAlmostEqual(sale_2.order_line[0].discount, 5)  # 10€ of 200€
        self.assertAlmostEqual(sale_2.order_line[0].discount1, 0)
        self.assertAlmostEqual(sale_2.order_line[0].discount_fixed, 10)
