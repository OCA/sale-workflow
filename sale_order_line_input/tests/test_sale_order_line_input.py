# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestSaleOrderLineInput(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )

    def test_sale_order_create_and_show(self):
        line_form = Form(
            self.env["sale.order.line"],
            view="sale_order_line_input.view_sales_order_line_input_tree",
        )
        line_form.order_partner_id = self.partner
        line_form.product_id = self.product
        line_form.price_unit = 190.50
        line_form.product_uom = self.env.ref("uom.product_uom_unit")
        line_form.product_uom_qty = 8.0
        line_form.name = "Test line description"
        line = line_form.save()
        self.assertTrue(line.order_id)
        action_dict = line.action_sale_order_form()
        self.assertEqual(action_dict["res_id"], line.order_id.id)
        self.assertEqual(action_dict["res_model"], "sale.order")

    def test_sale_order_line_compute_name(self):
        # Ensure that when calculating the line name, the new sales order id has
        # already been created as it is done in the order form view.
        line_form = Form(
            self.env["sale.order.line"],
            view="sale_order_line_input.view_sales_order_line_input_tree",
        )
        line_form.product_id = self.product

    def test_force_company_compute_and_onchange(self):
        """Test force_company_id compute and onchange behavior"""
        company = self.env.company

        line = self.env["sale.order.line"].new(
            {
                "product_id": self.product.id,
            }
        )

        # compute should fallback to env.company if no order
        line._compute_force_company_id()
        self.assertEqual(line.force_company_id, company)

        # onchange should propagate company
        line.force_company_id = company
        line._onchange_force_company_id()
        self.assertEqual(line.company_id, company)

    def test_onchange_order_partner_creates_order(self):
        """Ensure onchange creates a sale order when none exists"""
        line = self.env["sale.order.line"].new(
            {
                "order_partner_id": self.partner.id,
                "product_id": self.product.id,
            }
        )

        line._onchange_order_partner_id()

        self.assertTrue(line.order_id)
        self.assertEqual(line.order_id.partner_id, self.partner)

    def test_sale_order_sol_count(self):
        """Test compute of sol_count"""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )

        self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 2,
                "price_unit": 10,
            }
        )

        order._compute_sol_count()

        self.assertEqual(order.sol_count, 1)

    def test_action_view_sale_order_line(self):
        """Test smart button action for viewing order lines"""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )

        self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": 50,
            }
        )

        action = order.action_view_sale_order_line()

        self.assertEqual(action["res_model"], "sale.order.line")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["domain"], [("order_id", "=", order.id)])
