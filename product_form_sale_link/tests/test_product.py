from odoo.tests import TransactionCase
from odoo.tests.common import new_test_user, users


class TestProductSalesCount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_salesman = new_test_user(
            cls.env,
            login="test_salesman",
            groups="sales_team.group_sale_manager,sales_team.group_sale_salesman,base.group_user,base.group_partner_manager",
        )
        cls.user_employee = new_test_user(
            cls.env,
            login="test_employee",
            groups="base.group_user,product.group_product_manager",
        )
        cls.product1 = cls.env["product.product"].create({"name": "Test Product 1"})
        cls.product2 = cls.env["product.product"].create({"name": "Test Product 2"})
        cls.product_template = cls.product1.product_tmpl_id
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    @users("test_salesman")
    def test_product_variant_sales_count_with_salesman(self):
        self.sale_order.action_confirm()
        self.assertEqual(self.product1.sale_lines_count, 0)
        self.assertEqual(self.product2.sale_lines_count, 0)

    @users("test_employee")
    def test_product_variant_sales_count_without_access(self):
        self.sale_order.action_confirm()
        self.assertEqual(self.product1.sale_lines_count, 0)

    @users("test_salesman")
    def test_product_template_sales_count(self):
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale_order.id,
                    "product_id": self.product1.id,
                    "product_uom_qty": 1.0,
                },
                {
                    "order_id": self.sale_order.id,
                    "product_id": self.product2.id,
                    "product_uom_qty": 1.0,
                },
            ]
        )
        self.sale_order.action_confirm()
        self.assertEqual(self.product_template.sale_lines_count, 1)
