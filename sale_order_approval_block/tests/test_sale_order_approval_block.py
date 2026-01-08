# Copyright 2026 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrderApprovalBlock(TransactionCase):
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
        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "Partner 1",
                "email": "partner1@yourcompany.com",
                "company_id": cls.company1.id,
            }
        )

        # Products
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
            }
        )

        # Users
        cls.user1_id = cls._create_user(
            "user_sale_1", [cls.group_sale_user], cls.company1
        )
        cls.user2_id = cls._create_user(
            "user_sale_2", [cls.group_sale_manager], cls.company1
        )

        # Approval block reason
        cls._create_block_reason()

    @classmethod
    def _create_block_reason(cls):
        cls.so_approval_block_reason = cls.so_block_obj.create(
            {"name": "Needs Permission", "description": "Permission to confirm"}
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

    def _create_sale(self, line_products):
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
        sale = self.so_obj.create(
            {
                "partner_id": self.partner1.id,
                "order_line": lines,
                "company_id": self.company1.id,
            }
        )
        return sale
