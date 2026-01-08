from odoo.addons.base.tests.common import BaseCommon


class TestSoAmountBlock(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.users_obj = cls.env["res.users"]
        cls.so_obj = cls.env["sale.order"]
        cls.so_block_obj = cls.env["sale.approval.block.reason"]

        # company
        cls.company1 = cls.env.ref("base.main_company")

        # groups
        cls.group_sale_user = cls.env.ref("sales_team.group_sale_salesman_all_leads")
        cls.group_sale_manager = cls.env.ref("sales_team.group_sale_manager")

        # Partner
        cls.partner1 = cls.env["res.partner"].create({"name": "Customer"})

        # Products
        cls.product1 = cls.env["product.product"].create({"name": "Product 1"})
        cls.product2 = cls.env["product.product"].create({"name": "Product 2"})
        cls.product3 = cls.env["product.product"].create({"name": "Product 3"})

        # Users
        cls.user1_id = cls._create_user(
            "user_sale_1", [cls.group_sale_user], cls.company1
        )
        cls.user2_id = cls._create_user(
            "user_sale_2", [cls.group_sale_manager], cls.company1
        )

    @classmethod
    def _create_user(cls, login, groups, company):
        group_ids = [group.id for group in groups]
        user = cls.users_obj.with_context(no_reset_password=True).create(
            {
                "name": "Sale User",
                "login": login,
                "password": "test",
                "email": "test@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "group_ids": [(6, 0, group_ids)],
            }
        )
        return user.id

    @classmethod
    def _create_sale(cls, line_products):
        lines = []
        for product, qty in line_products:
            lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "price_unit": 100,
                    },
                )
            )
        sale = cls.so_obj.create(
            {
                "partner_id": cls.partner1.id,
                "order_line": lines,
                "company_id": cls.company1.id,
            }
        )
        return sale

    def test_so_amount_block_under_minimum_manager_release(self):
        self.partner1.write({"minimum_so_amount": 1500.0})

        sale = self._create_sale(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )

        self.assertEqual(
            sale.approval_block_id,
            self.env.ref("sale_minimum_amount.minimum_amount_block_reason"),
        )

        sale.with_user(self.user1_id).action_confirm()
        self.assertEqual(sale.state, "draft")

        sale.with_user(self.user2_id).button_release_approval_block()
        sale.action_confirm()
        self.assertEqual(sale.state, "sale")

    def test_so_amount_block_above_minimum(self):
        self.partner1.write({"minimum_so_amount": 1500.0})

        sale = self._create_sale(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )

        self.assertTrue(sale.approval_block_id)

        for line in sale.order_line:
            if line.product_id == self.product1:
                line.product_uom_qty = 10
                line.price_unit = 100

        sale.flush_recordset()
        self.assertFalse(sale.approval_block_id)

        sale.with_user(self.user1_id).action_confirm()
        self.assertEqual(sale.state, "sale")

    def test_so_amount_block_minimum_zero(self):
        self.partner1.write({"minimum_so_amount": 0.0})
        sale = self._create_sale([(self.product1, 1)])
        self.assertFalse(sale.approval_block_id)
        sale.with_user(self.user1_id).action_confirm()
        self.assertEqual(sale.state, "sale")

    def test_so_amount_block_partner_change(self):
        partner2 = self.env["res.partner"].create(
            {"name": "Customer 2", "minimum_so_amount": 1500.0}
        )
        self.partner1.write({"minimum_so_amount": 500.0})
        sale = self._create_sale([(self.product1, 6)])
        self.assertFalse(sale.approval_block_id)
        sale.write({"partner_id": partner2.id})
        self.assertEqual(
            sale.approval_block_id,
            self.env.ref("sale_minimum_amount.minimum_amount_block_reason"),
        )
        sale.write({"partner_id": self.partner1.id})
        self.assertFalse(sale.approval_block_id)
