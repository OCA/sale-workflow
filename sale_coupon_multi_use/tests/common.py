# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase

DISCOUNT_AMOUNT = 5000


class TestSaleCouponMultiUseCommon(SavepointCase):
    """Common class for multi use coupon tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for multi use coupon tests."""
        super().setUpClass()
        # Models.
        cls.SaleCoupon = cls.env["sale.coupon"]
        cls.SaleCouponProgram = cls.env["sale.coupon.program"]
        cls.SaleCouponGenerate = cls.env["sale.coupon.generate"]
        cls.SaleCouponApplyCode = cls.env["sale.coupon.apply.code"]
        # Programs.
        cls.program_coupon_percentage = cls.env.ref("sale_coupon.10_percent_coupon")
        # Sales.
        # amount_total = 9705
        cls.sale_1 = cls.env.ref("sale.sale_order_1")
        # amount_total = 2947.5
        cls.sale_2 = cls.env.ref("sale.sale_order_2")
        cls.program_multi_use = cls.SaleCouponProgram.create(
            {
                "name": "Multi Use Coupon Program",
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": DISCOUNT_AMOUNT,
                "coupon_multi_use": True,
            }
        )
        # Generate one coupon for usage.
        cls.coupon_generate_wiz = cls.SaleCouponGenerate.with_context(
            active_id=cls.program_multi_use.id
        ).create({})
        cls.coupon_generate_wiz.generate_coupon()
        cls.coupon_multi_use_1 = cls.program_multi_use.coupon_ids[0]
        # Prepare coupon apply wizard.
        cls.coupon_apply_wiz = cls.SaleCouponApplyCode.create(
            {"coupon_code": cls.coupon_multi_use_1.code}
        )
        cls.company_main = cls.env.ref("base.main_company")
        cls.eur = cls.env.ref("base.EUR")
        cls.usd = cls.env.ref("base.USD")
        cls.pricelist_public = cls.env.ref("product.list0")
