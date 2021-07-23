# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common


class TestSaleCouponCriteriaMultiProduct(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_obj = cls.env["product.product"]
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Mr. Odoo", "property_product_pricelist": cls.pricelist.id}
        )
        cls.product_a = product_obj.create({"name": "Product A", "list_price": 50})
        coupon_program_form = Form(
            cls.env["sale.coupon.program"],
            view="sale_coupon.sale_coupon_program_view_promo_program_form",
        )
        coupon_program_form.name = "Test Program"
        coupon_program_form.promo_code_usage = "no_code_needed"
        coupon_program_form.reward_type = "discount"
        coupon_program_form.discount_apply_on = "on_order"
        coupon_program_form.discount_type = "percentage"
        coupon_program_form.discount_percentage = 10
        coupon_program_form.rule_products_domain = "[('id', '=', %s)]" % (
            cls.product_a.id
        )
        cls.coupon_program = coupon_program_form.save()
        # We'll be using this sale order
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product_a
            line_form.product_uom_qty = 1
        cls.sale = sale_form.save()

    def test_coupon_order_line_link(self):
        """The coupon program gets correctly linked to the line"""
        self.sale.recompute_coupon_lines()
        discount_line = self.sale.order_line.filtered("is_reward_line")
        self.assertEqual(discount_line.coupon_program_id, self.coupon_program)
