# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged
from odoo.tests.common import new_test_user, users

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleOrderLineDescriptionChange(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create models
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_order_line_model = cls.env["sale.order.line"]
        cls.partner_model = cls.env["res.partner"]
        cls.product_model = cls.env["product.product"]
        cls.env["res.config.settings"].create(
            {"group_use_product_description_per_so_line": True}
        ).execute()
        new_test_user(
            cls.env,
            login="test_sale_description_only",
            groups="sales_team.group_sale_manager",
            context={"no_reset_password": True, "mail_create_nosubscribe": True},
        )

        # Create the sale order
        cls.partner = cls.partner_model.create({"name": "Test partner"})
        cls.sale_order = cls.sale_order_model.create({"partner_id": cls.partner.id})

        cls.product = cls.product_model.create(
            {
                "name": "Test product",
                "description_sale": "Sale description for test product",
            }
        )

    @users("test_sale_description_only")
    def test_check_only_sale_order_line_description(self):
        sale_order_line = self.sale_order_line_model.create(
            {"order_id": self.sale_order.id, "product_id": self.product.id}
        )
        self.assertEqual(
            sale_order_line.name,
            self.product.description_sale,
            "Enabling the product-description-only setting does not modify sale order "
            "line description",
        )

    @users("test_sale_description_only")
    def test_manual_description_edit_keeps_product_name_hidden(self):
        with Form(self.sale_order_model) as order_form:
            order_form.partner_id = self.partner
            with order_form.order_line.new() as line_form:
                line_form.product_id = self.product
                line_form.name = f"{self.product.description_sale} test"
        sale_order = order_form.save()

        self.assertEqual(
            sale_order.order_line.name, f"{self.product.description_sale} test"
        )
