# Copyright 2019 Akretion
# Update (Migration) 2022 Ooops - Ashish Hirpara <hello@ashish-hirpara.com>
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
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
                "manual_force_sale_min_qty": "use_parent",
                "manual_sale_max_qty": 100.0,
                "manual_force_sale_max_qty": "use_parent",
                "manual_sale_multiple_qty": 5.0,
            }
        )

        self.categ = self.product_categ_model.create(
            {
                "name": "Test categ",
                "parent_id": self.categ_parent.id,
                "manual_force_sale_min_qty": "use_parent",
                "manual_force_sale_max_qty": "use_parent",
            }
        )

        self.product = self.product_model.create(
            {
                "name": "Test product",
                "force_sale_min_qty": False,
                "force_sale_max_qty": False,
            }
        )

    def test_check_sale_order_min_qty_required(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 5.0}
        self.product.manual_sale_min_qty = 10
        # Create sale order line with Qty less than min Qty
        with self.assertRaises(ValidationError):
            self.sale_order_model.create(
                {
                    "partner_id": self.partner.id,
                    "order_line": [(0, 0, line_values)],
                    "pricelist_id": 1,
                }
            )
        line_values["product_uom_qty"] = 12.0
        # Create sale order line with Qty great then min Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.sale_order.order_line._compute_sale_restricted_qty()
        self.assertFalse(self.sale_order.order_line.is_qty_less_min_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 12.0)

    def test_check_sale_order_min_qty_recommended(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 5.0}
        self.product.manual_sale_min_qty = 10
        # Set Force min Qty to true
        self.product.manual_force_sale_min_qty = "force"

        # Create sale order line with Qty less than min Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.sale_order.order_line._compute_sale_restricted_qty()
        self.assertTrue(self.sale_order.order_line.is_qty_less_min_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 5.0)

    def test_check_sale_order_max_qty_required(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 15.0}
        self.product.manual_sale_max_qty = 10
        # Create sale order line with Qty bigger than max Qty
        with self.assertRaises(ValidationError):
            sale_order = self.sale_order_model.create(
                {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
            )
            sale_values = self.refrech_sale_values(sale_order)
            self.sale_order_model.create(sale_values)
        line_values["product_uom_qty"] = 2.0
        # Create sale order line with Qty great then max Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.sale_order.order_line._compute_sale_restricted_qty()
        self.assertFalse(self.sale_order.order_line.is_qty_bigger_max_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 2.0)

    def test_check_sale_order_max_qty_recommended(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 15.0}
        self.product.manual_sale_max_qty = 10
        # Set Force max Qty to true
        self.product.manual_force_sale_max_qty = "force"

        # Create sale order line with Qty bigger than max Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.sale_order.order_line._compute_sale_restricted_qty()
        self.assertTrue(self.sale_order.order_line.is_qty_bigger_max_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 15.0)

    def test_check_sale_order_multiple_qty_required(self):
        line_values = {"product_id": self.product.id, "product_uom_qty": 15.0}
        self.product.manual_sale_min_qty = 10
        self.product.manual_sale_multiple_qty = 10
        # Create sale order line with Qty not multiple Qty
        with self.assertRaises(ValidationError):
            sale_order = self.sale_order_model.create(
                {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
            )
            sale_values = self.refrech_sale_values(sale_order)
            self.sale_order_model.create(sale_values)
        line_values["product_uom_qty"] = 20
        # Create sale order line with Qty multiple Qty
        self.sale_order = self.sale_order_model.create(
            {"partner_id": self.partner.id, "order_line": [(0, 0, line_values)]}
        )
        self.sale_order.order_line._compute_sale_restricted_qty()
        self.assertFalse(self.sale_order.order_line.is_qty_not_multiple_qty)

        self.assertEqual(self.sale_order.order_line.product_uom_qty, 20)

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
