# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestSaleAnalyticGlobal(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan"})
        cls.product = cls.env.ref("product.product_product_4")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        vals_list = [
            {"name": "Analytic Account 1", "plan_id": cls.analytic_plan.id},
            {"name": "Analytic Account 2", "plan_id": cls.analytic_plan.id},
            {"name": "Analytic Account 3", "plan_id": cls.analytic_plan.id},
        ]
        cls.account1, cls.account2, cls.account3 = cls.env[
            "account.analytic.account"
        ].create(vals_list)
        cls.sale_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        line_vals_list = [
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "order_id": cls.sale_order.id,
                "product_uom_qty": 10,
                "price_unit": 50,
                "product_uom": cls.product.uom_id.id,
            }
            for _ in range(3)
        ]
        cls.order_line = cls.env["sale.order.line"].create(line_vals_list)
        cls.line1, cls.line2, cls.line3 = cls.order_line

    def test_00_sale_order_compute_distribution(self):
        """Test the analytic distribution is computed correctly.

        1. Check the analytic distribution is the same on order lines
        and is set on the sale order.
        2. Check the analytic distribution is different on order lines
        and is not set on the sale order.
        3. Check no distribution on order lines and on the sale order.
        """
        self.assertFalse(
            any(self.sale_order.order_line.mapped("analytic_distribution")),
            "No distribution",
        )
        self.assertFalse(self.sale_order.analytic_distribution, "No distribution")
        self.order_line.analytic_distribution = {self.account1.id: 25}
        self.assertEqual(
            self.sale_order.analytic_distribution,
            {str(self.account1.id): 25.0},
            "Same distribution",
        )
        self.line2.analytic_distribution = {self.account2.id: 50}
        self.line3.analytic_distribution = False
        self.assertFalse(
            self.sale_order.analytic_distribution, "Different distribution"
        )
        # Set the same distribution on the order lines
        self.order_line.analytic_distribution = {self.account3.id: 55}
        self.assertEqual(
            self.sale_order.analytic_distribution,
            {str(self.account3.id): 55.0},
            "Same distribution",
        )
        # Remove the distribution on the order lines
        self.order_line.analytic_distribution = False
        self.assertFalse(self.sale_order.analytic_distribution, "No distribution")

    def test_01_sale_order_inverse_distribution(self):
        """Test the analytic distribution is inversed correctly.

        Check distribution set on the sale order
        is propagated to order lines.
        """
        self.assertFalse(
            any(self.sale_order.order_line.mapped("analytic_distribution")),
            "No distribution",
        )
        self.sale_order.analytic_distribution = {self.account1.id: 50}
        self.assertTrue(
            all(
                line.analytic_distribution == self.sale_order.analytic_distribution
                for line in self.sale_order.order_line
            ),
            "Same distribution",
        )
