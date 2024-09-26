# Import Odoo libs
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSaleBlanketOrdersTierValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blanket_order_obj = cls.env["sale.blanket.order"]
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.payment_term = cls.env.ref("account.account_payment_term_immediate")
        cls.sale_pricelist = cls.env["product.pricelist"].create(
            {"name": "Test Pricelist", "currency_id": cls.env.ref("base.USD").id}
        )

        # UoM
        cls.categ_unit = cls.env.ref("uom.product_uom_categ_unit")
        cls.uom_dozen = cls.env["uom.uom"].create(
            {
                "name": "Test-DozenA",
                "category_id": cls.categ_unit.id,
                "factor_inv": 12,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "TEST CUSTOMER",
                "property_product_pricelist": cls.sale_pricelist.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Demo",
                "categ_id": cls.env.ref("product.product_category_1").id,
                "standard_price": 35.0,
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "PROD_DEL01",
            }
        )

        cls.yesterday = date.today() - timedelta(days=1)
        cls.tomorrow = date.today() + timedelta(days=1)

        cls.test_user_1 = cls.env["res.users"].create(
            {
                "name": "user_sale_manager",
                "login": "user_sale_manager",
                "groups_id": [
                    (6, 0, [cls.env.ref("sales_team.group_sale_manager").id])
                ],
            }
        )

        cls.eco_model = cls.env.ref(
            "sale_blanket_order_tier_validation.model_sale_blanket_order"
        )
        # Create tier definition for this test
        cls.tier_def_obj.create(
            {
                "model_id": cls.eco_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
            }
        )

    def test01_tier_validation_model_name(self):
        """
        Tests to ensure that the sale.blanket.order model is now part of the options
          on a tier definition.
        """
        self.assertIn(
            "sale.blanket.order", self.tier_def_obj._get_tier_validation_model_names()
        )

    def test02_validation_blanket_order(self):
        # Create an Sale blanket order in the 'draft' stage
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 10.0,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(blanket_order.state, "draft")
        blanket_order.flush_recordset()

        # Request tier validation
        blanket_order.request_validation()

        # Changing to new stage would cause a validation error
        with self.assertRaises(ValidationError):
            blanket_order.action_confirm()
            blanket_order.flush_recordset()

        # Validate the tier validation request
        blanket_order.with_user(self.test_user_1).validate_tier()
        self.assertTrue(blanket_order.validated)

        # Change the sale blanket stage to normal
        blanket_order.action_confirm()

        # Confirm the stage changed
        self.assertEqual(blanket_order.state, "open")
