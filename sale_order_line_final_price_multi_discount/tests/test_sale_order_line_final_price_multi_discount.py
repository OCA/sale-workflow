# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form, new_test_user, tagged

from odoo.addons.sale_multi_discount.tests.common import SaleMultiDiscountCommon

from ..models.sale_order_line import POLICY_PARAM, UNLOCK_PARAM


@tagged("post_install", "-at_install")
class TestSaleOrderLineFinalPriceMultiDiscount(SaleMultiDiscountCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The expected figures below depend on these precisions
        cls.env.ref("product.decimal_price").digits = 2
        cls.env.ref("product.decimal_discount").digits = 2
        # Pricelist discounts are shown when the option is on for everybody,
        # as the settings do (product.pricelist.item reads it on the superuser)
        cls.env.ref("base.group_user").implied_ids += cls.group_discount_per_so_line
        cls.product_100 = cls.env["product.product"].create(
            {
                "name": "Final price product",
                "type": "consu",
                "list_price": 100.0,
                "taxes_id": False,
            }
        )
        cls.product_free = cls.env["product.product"].create(
            {
                "name": "Final price product free",
                "type": "consu",
                "list_price": 0.0,
                "taxes_id": False,
            }
        )
        cls.icp = cls.env["ir.config_parameter"].sudo()

    def _line(self, product=None, pricelist=None, **vals):
        order_vals = {
            "partner_id": self.partner.id,
            "order_line": [
                Command.create({"product_id": (product or self.product_100).id, **vals})
            ],
        }
        if pricelist:
            order_vals["pricelist_id"] = pricelist.id
        return self.env["sale.order"].create(order_vals).order_line

    def test_final_price_sets_distribution(self):
        line = self._line()
        line.price_final = 80
        self.assertEqual(line.price_unit, 100)
        self.assertEqual(line.discount_distribution, [20.0])
        self.assertAlmostEqual(line.discount, 20.0)
        self.assertAlmostEqual(line.price_subtotal, 80.0)

    def test_final_price_over_unit_price(self):
        line = self._line()
        line.price_final = 120
        self.assertEqual(line.price_unit, 100)
        self.assertEqual(line.discount_distribution, [-20.0])
        self.assertAlmostEqual(line.price_subtotal, 120.0)

    def test_final_price_follows_distribution(self):
        line = self._line()
        line.discount_distribution = [10, 5]
        self.assertAlmostEqual(line.price_final, 85.5)

    def test_final_price_shows_reachable_figure(self):
        line = self._line(price_unit=1000)
        line.price_final = 333.33
        self.assertEqual(line.discount_distribution, [66.67])
        self.assertAlmostEqual(line.price_final, 333.30)

    def test_final_price_shows_reachable_figure_on_create(self):
        line = self._line(price_unit=1000, price_final=333.33)
        self.assertEqual(line.price_unit, 1000)
        self.assertEqual(line.discount_distribution, [66.67])
        self.assertAlmostEqual(line.discount, 66.67)
        self.assertAlmostEqual(line.price_final, 333.30)
        self.assertAlmostEqual(line.price_subtotal, 333.30)

    def test_final_price_in_form(self):
        line = self._line()
        with Form(line.order_id) as order_form:
            with order_form.order_line.edit(0) as line_form:
                line_form.price_final = 75
                self.assertEqual(line_form.discount_distribution, [25.0])
        self.assertEqual(line.discount_distribution, [25.0])
        self.assertAlmostEqual(line.price_subtotal, 75.0)

    def test_final_price_without_unit_price(self):
        line = self._line(product=self.product_free)
        line.price_final = 50
        self.assertEqual(line.price_unit, 50)
        self.assertFalse(line.discount_distribution)
        self.assertAlmostEqual(line.price_subtotal, 50.0)

    def test_append_to_pricelist_discounts(self):
        self.icp.set_param(POLICY_PARAM, "append")
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Ten percent off",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.product_100.id,
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                        }
                    )
                ],
            }
        )
        line = self._line(pricelist=pricelist)
        self.assertEqual(line.discount_distribution, [10.0])
        line.price_final = 72
        # 100 x 0.90 x 0.80 = 72
        self.assertEqual(line.discount_distribution, [10.0, 20.0])
        self.assertAlmostEqual(line.price_subtotal, 72.0)

    def test_replace_pricelist_discounts(self):
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Ten percent off",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.product_100.id,
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                        }
                    )
                ],
            }
        )
        line = self._line(pricelist=pricelist)
        line.price_final = 72
        self.assertEqual(line.discount_distribution, [28.0])

    def test_lock_and_unlock(self):
        salesman = new_test_user(
            self.env,
            login="final-price-multi-salesman",
            groups="sales_team.group_sale_salesman,sale.group_discount_per_so_line",
        )
        line = (
            self._line()
            .with_user(salesman)
            .with_context(test_sale_order_line_final_price=True)
        )
        # Locked by default, as in sale_order_line_final_price
        self.icp.set_param(UNLOCK_PARAM, False)
        line.invalidate_recordset(["price_edit_allowed"])
        self.assertFalse(line.price_edit_allowed)
        self.icp.set_param(UNLOCK_PARAM, True)
        line.invalidate_recordset(["price_edit_allowed"])
        self.assertTrue(line.price_edit_allowed)
        # A parameter typed by hand is read as a boolean, not as a string
        self.icp.set_param(UNLOCK_PARAM, "False")
        line.invalidate_recordset(["price_edit_allowed"])
        self.assertFalse(line.price_edit_allowed)
