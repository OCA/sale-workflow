# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError


@common.at_install(False)
@common.post_install(True)
class TestSaleOrderLineMinQty(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineMinQty, self).setUp()

        # Create models
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]
        self.partner_model = self.env["res.partner"]
        self.product_categ_model = self.env["product.category"]
        self.product_model = self.env["product.product"]
        self.sale_order = self.sale_order_model
        # Create partner and product
        self.partner = self.partner_model.create({"name": "Test partner"})
        self.categ_parent = self.product_categ_model.create(
            {
                "name": "Test Parent categ",
                "manual_sale_min_qty": 10.0,
                "manual_force_sale_min_qty": False,
                "manual_sale_multiple_qty": 5.0,
            }
        )

        self.categ = self.product_categ_model.create(
            {
                "name": "Test categ",
                "parent_id": self.categ_parent.id,
                "manual_force_sale_min_qty": False,
            }
        )

        self.product = self.product_model.create(
            {"name": "Test product", "force_sale_min_qty": False}
        )

    def test_check_sale_order_min_qty_required(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 5.0}
        self.product.manual_sale_min_qty = 10
        # Create sale order line with Qty less than min Qty
        with self.assertRaises(ValidationError):
            self.sale_order = self.sale_order_model.create(
                {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
            )
        line_values["product_uom_qty"] = 12.0
        # Create sale order line with Qty great then min Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.assertFalse(self.sale_order.order_line.is_qty_less_min_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 12.0)

    def test_check_sale_order_min_qty_recommended(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 5.0}
        self.product.manual_sale_min_qty = 10
        # Set Force min Qty to true
        self.product.force_sale_min_qty = True

        # Create sale order line with Qty less than min Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.assertTrue(self.sale_order.order_line.is_qty_less_min_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 5.0)

    def test_check_sale_order_multiple_qty_required(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 15.0}
        self.product.manual_sale_min_qty = 10
        self.product.manual_sale_multiple_qty = 10
        # Create sale order line with Qty not multiple Qty
        with self.assertRaises(ValidationError):
            self.sale_order = self.sale_order_model.create(
                {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
            )
        line_values["product_uom_qty"] = 20
        # Create sale order line with Qty multiple Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.assertFalse(self.sale_order.order_line.is_qty_not_multiple_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 20)

    def test_check_min_multiple_qty_category_hierarchy(self):
        # Check min and  multiple Qty from parent category
        self.product.categ_id = self.categ
        self.assertEqual(self.product.manual_sale_min_qty, 0)
        self.assertEqual(self.product.manual_sale_multiple_qty, 0)
        self.product.categ_id.parent_id._compute_sale_min_qty()
        self.product.categ_id.parent_id._compute_sale_multiple_qty()

        self.product._compute_sale_min_qty()
        self.assertEqual(self.product.sale_min_qty, 10)
        self.assertEqual(self.product.sale_multiple_qty, 5)
        self.categ_parent.manual_force_sale_min_qty = True
        self.product.categ_id.parent_id._compute_force_sale_min_qty()
        self.product._compute_force_sale_min_qty()
        # import pdb; pdb.set_trace()
        self.assertEqual(self.product.manual_force_sale_min_qty, False)
        self.assertEqual(self.product.force_sale_min_qty, True)
        # Check min and  multiple Qty from category
        self.categ.manual_sale_min_qty = 15
        self.categ.manual_sale_multiple_qty = 10
        self.product._compute_sale_min_qty()
        self.product._compute_sale_multiple_qty()
        self.assertEqual(self.product.sale_min_qty, 15)
        self.assertEqual(self.product.sale_multiple_qty, 10)

    def test_check_min_multiple_qty_tmpl_hierarchy(self):
        # Check min and  multiple Qty from product template
        self.product.manual_sale_min_qty_tmpl = 20
        self.product.manual_sale_multiple_qty_tmpl = 30
        self.product.product_tmpl_id._compute_sale_min_qty_tmpl()
        self.product.product_tmpl_id._compute_sale_multiple_qty_tmpl()
        self.assertEqual(self.product.manual_sale_min_qty, 0)
        self.assertEqual(self.product.sale_min_qty, 20)
        self.assertEqual(self.product.manual_sale_multiple_qty, 0)
        self.assertEqual(self.product.sale_multiple_qty, 30)
        # Check min and  multiple Qty from product
        self.product.manual_sale_min_qty = 25
        self.product.manual_sale_multiple_qty = 25
        # self.product._compute_sale_min_qty()
        # self.product._compute_sale_multiple_qty()
        self.assertEqual(self.product.sale_min_qty, 25)
        self.assertEqual(self.product.sale_multiple_qty, 25)
