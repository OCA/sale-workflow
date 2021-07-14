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
        cls.product_b = product_obj.create({"name": "Product B", "list_price": 60})
        cls.product_c = product_obj.create({"name": "Product C", "list_price": 70})
        cls.product_d = product_obj.create({"name": "Product A", "list_price": 80})
        cls.product_e = product_obj.create({"name": "Product E", "list_price": 70})
        cls.product_f = product_obj.create({"name": "Product F", "list_price": 60})
        coupon_program_form = Form(
            cls.env["sale.coupon.program"],
            view="sale_coupon.sale_coupon_program_view_promo_program_form",
        )
        coupon_program_form.name = "Test Criteria Multi Product Program"
        coupon_program_form.promo_code_usage = "no_code_needed"
        coupon_program_form.reward_type = "discount"
        coupon_program_form.discount_apply_on = "on_order"
        coupon_program_form.discount_type = "percentage"
        coupon_program_form.discount_percentage = 10
        coupon_program_form.sale_coupon_criteria = "multi_product"
        # This is the set of criterias that the order must fulfill for the program to
        # be applied.
        #  Qty |    Products    | Repeat
        # -----|----------------|--------
        #    1 | Prod A         |
        #    2 | Prod B, Prod C |
        #    3 | Prod D, Prod E |  Yes
        with coupon_program_form.sale_coupon_criteria_ids.new() as criteria:
            criteria.product_ids.add(cls.product_a)
        with coupon_program_form.sale_coupon_criteria_ids.new() as criteria:
            criteria.product_ids.add(cls.product_b)
            criteria.product_ids.add(cls.product_c)
        with coupon_program_form.sale_coupon_criteria_ids.new() as criteria:
            criteria.repeat_product = True
            criteria.product_ids.add(cls.product_d)
            criteria.product_ids.add(cls.product_e)
            criteria.rule_min_quantity = 3
        cls.coupon_program = coupon_program_form.save()
        # We'll be using this sale order
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product_a
            line_form.product_uom_qty = 1
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product_b
            line_form.product_uom_qty = 1
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product_c
            line_form.product_uom_qty = 2
        with sale_form.order_line.new() as line_form:
            line_form.product_id = cls.product_e
            line_form.product_uom_qty = 3
        cls.sale = sale_form.save()

    def test_sale_coupon_test_criteria_multi_product(self):
        """Only when all the criterias are matched we can apply the program"""
        # The discount is correctly applied
        self.sale.recompute_coupon_lines()
        discount_line = self.sale.order_line.filtered("is_reward_line")
        self.assertTrue(bool(discount_line))
        # We can change product E by product D as the criteria is set to repeat
        line_e = self.sale.order_line.filtered(lambda x: x.product_id == self.product_e)
        line_e.product_id = self.product_d
        self.sale.recompute_coupon_lines()
        discount_line = self.sale.order_line.filtered("is_reward_line")
        self.assertTrue(bool(discount_line))
        # If the order doesn't fulfill all the criterias, the discount isn't applied
        line_e.product_uom_qty = 2
        self.sale.recompute_coupon_lines()
        discount_line = self.sale.order_line.filtered("is_reward_line")
        self.assertFalse(discount_line)
        # If the criteria doesn't repeat, all the products must be in the cart
        # Lets recover the former line qtys:
        line_e.product_uom_qty = 3
        # And now we'll remove B, that should be present
        self.sale.order_line.filtered(lambda x: x.product_id == self.product_b).unlink()
        self.sale.recompute_coupon_lines()
        discount_line = self.sale.order_line.filtered("is_reward_line")
        self.assertFalse(discount_line)
