# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSaleOrderLineDescriptionChange(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineDescriptionChange, self).setUp()

        # Create models
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]
        self.partner_model = self.env["res.partner"]
        self.product_model = self.env["product.product"]
        self.user_model = self.env["res.users"].with_context(
            {"no_reset_password": True, "mail_create_nosubscribe": True}
        )

        # Create two different users
        self.group_only_sale_description = self.env.ref(
            "sale_order_line_description.group_use_product_description_per_so_line"
        )
        self.user_1 = self._create_user("TestUser1")
        self.user_2 = self._create_user("TestUser2", self.group_only_sale_description)

        # Create the sale order
        self.partner = self.partner_model.create({"name": "Test partner"})
        self.sale_order = self.sale_order_model.create({"partner_id": self.partner.id})

        self.product = self.product_model.create(
            {
                "name": "Test product",
                "description_sale": "Sale description for test product",
            }
        )

    def _create_user(self, name, group=None):
        groups_id = self.env.user.groups_id
        if group:
            groups_id += group
        return self.user_model.create(
            {
                "name": name,
                "login": name,
                "email": name + "@example.com",
                "groups_id": groups_id,
            }
        )

    def test_check_sale_order_line_description(self):
        line_values = {"order_id": self.sale_order.id, "product_id": self.product.id}

        # Create sale order line with TestUser1
        sale_order_line = self.sale_order_line_model.with_user(self.user_1).create(
            line_values.copy()
        )
        self.assertEqual(
            sale_order_line.name,
            "\n".join([self.product.name, self.product.description_sale]),
            "Standard behavior does not concatenate "
            "product description and product sale description",
        )

        # Create sale order line with TestUser2
        sale_order_line = self.sale_order_line_model.with_user(self.user_2).create(
            line_values.copy()
        )
        self.assertEqual(
            sale_order_line.name,
            self.product.description_sale,
            "Adding group "
            + self.group_only_sale_description.name
            + " does not modify sale order line description",
        )
