# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase

NAME_COUPON_PROGRAM = "Dummy Coupon Program"
CODE_COUPON_PROGRAM = "MYCODE123"


class TestSaleCouponProductManageCommon(SavepointCase):
    """Common class for program product tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for multi use coupon tests."""
        super().setUpClass()
        # Models.
        cls.SaleCouponProgram = cls.env["sale.coupon.program"]
        cls.ProductCategory = cls.env["product.category"]
        # Records.
        cls.product_category_not_program = cls.ProductCategory.create(
            {"name": "Dummy Not Program Category", "is_program_category": False}
        )
        cls.product_category_program = cls.ProductCategory.create(
            {"name": "Dummy Program Category", "is_program_category": True}
        )
        cls.product_category_program_default = cls.ProductCategory.create(
            {"name": "Dummy Program Category Default", "is_program_category": True}
        )
        cls.program = cls.SaleCouponProgram.create(
            {
                "name": NAME_COUPON_PROGRAM,
                "program_type": "coupon_program",
                "reward_type": "discount",
                "discount_type": "fixed_amount",
                "discount_fixed_amount": 1000,
                "force_product_default_code": CODE_COUPON_PROGRAM,
                "force_product_categ_id": cls.product_category_program.id,
            }
        )
