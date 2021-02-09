# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("-at_install", "post_install")
class TestSaleOrderLineMinQty(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineMinQty, self).setUp()
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.categ_parent = self.env["product.category"].create(
            {
                "name": "Test Parent categ",
                "manual_sale_min_qty": 10.0,
                "manual_force_sale_min_qty": "use_parent",
                "manual_sale_max_qty": 100.0,
                "manual_force_sale_max_qty": "use_parent",
                "manual_sale_multiple_qty": 5.0,
            }
        )
        self.categ = self.env["product.category"].create(
            {
                "name": "Test categ",
                "parent_id": self.categ_parent.id,
                "manual_force_sale_min_qty": "use_parent",
                "manual_force_sale_max_qty": "use_parent",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test product",
                "force_sale_min_qty": False,
                "force_sale_max_qty": False,
                "categ_id": self.categ.id,
            }
        )
        self.sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.line = self.env["sale.order.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 20.0,
                "order_id": self.sale_order.id,
            }
        )

    def test_qty_bounds_no_force(self):
        """
        Successive tests of validity for min, max, multiple
        """
        with self.assertRaises(ValidationError) as e:
            self.line.product_uom_qty = 1.0
        self.assertIn("Higher quantity required!", e.exception.name)
        with self.assertRaises(ValidationError) as e:
            self.line.product_uom_qty = 200.0
        self.assertIn("Lower quantity required!", e.exception.name)
        with self.assertRaises(ValidationError) as e:
            self.line.product_uom_qty = 12.0
        self.assertIn("Correct multiple of quantity required!", e.exception.name)

    def test_qty_bounds_force(self):
        """
        Successive tests of validity for min, max, multiple
        + Force constraints to be optional
        """
        self.product.force_sale_min_qty = True
        self.product.force_sale_max_qty = True
        self.line._compute_sale_restricted_qty()
        self.line.product_uom_qty = 5.0
        self.assertFalse(self.line.qty_invalid)
        self.assertIn(self.line.qty_warning_message, "Higher quantity recommended!")
        self.line.product_uom_qty = 200.0
        self.assertFalse(self.line.qty_invalid)
        self.assertIn(self.line.qty_warning_message, "Lower quantity recommended!")

    def test_check_restricted_qty_category_hierarchy(self):
        # Check Restricted Qty from parent category
        self.product.categ_id = self.categ
        self.assertEqual(self.product.manual_sale_min_qty, 0)
        self.assertEqual(self.product.manual_sale_multiple_qty, 0)
        self.product.categ_id.parent_id._compute_sale_restricted_qty()

        self.assertEqual(self.product.sale_min_qty, 10)
        self.assertEqual(self.product.sale_max_qty, 100)
        self.assertEqual(self.product.sale_multiple_qty, 5)
        self.categ_parent.manual_force_sale_min_qty = "force"
        self.assertEqual(self.product.manual_force_sale_min_qty, "use_parent")
        self.assertEqual(self.product.force_sale_min_qty, True)
        # Check Restricted Qty from category
        self.categ.manual_sale_min_qty = 15
        self.categ.manual_sale_multiple_qty = 10
        self.categ.manual_force_sale_min_qty = "not_force"
        self.assertEqual(self.product.sale_min_qty, 15)
        self.assertEqual(self.product.sale_multiple_qty, 10)
        self.assertEqual(self.product.force_sale_min_qty, False)
        self.categ.manual_sale_max_qty = 200
        self.categ.manual_force_sale_max_qty = "not_force"
        self.assertEqual(self.product.sale_max_qty, 200)
        self.assertEqual(self.product.force_sale_max_qty, False)

    def test_check_restricted_qty_tmpl_hierarchy(self):
        # Check Restricted from product template
        self.product.product_tmpl_id.manual_sale_min_qty = 20
        self.product.product_tmpl_id.manual_sale_max_qty = 250
        self.product.product_tmpl_id.manual_sale_multiple_qty = 30
        self.product.product_tmpl_id._compute_sale_restricted_qty()
        self.assertEqual(self.product.manual_sale_min_qty, 0)
        self.assertEqual(self.product.sale_min_qty, 20)
        self.assertEqual(self.product.manual_sale_max_qty, 0)
        self.assertEqual(self.product.sale_max_qty, 250)
        self.assertEqual(self.product.manual_sale_multiple_qty, 0)
        self.assertEqual(self.product.sale_multiple_qty, 30)
        # Check Restricted Qty from product
        self.product.manual_sale_min_qty = 25
        self.product.manual_sale_max_qty = 150
        self.product.manual_sale_multiple_qty = 25
        self.assertEqual(self.product.sale_min_qty, 25)
        self.assertEqual(self.product.sale_max_qty, 150)
        self.assertEqual(self.product.sale_multiple_qty, 25)

    def test_action_refresh_restricted_qty(self):
        self.product.manual_sale_min_qty = 30.0
        self.sale_order.action_refresh_qty_restrictions()
        self.assertTrue(self.sale_order.qty_invalid)

    def test_search_qty_invalid(self):
        self.product.manual_sale_min_qty = 30.0
        self.sale_order.action_refresh_qty_restrictions()
        self.assertEqual(
            self.sale_order, self.env["sale.order"].search([("qty_invalid", "=", True)])
        )
