# Copyright 2026 Moduon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests import HttpCase, tagged
from odoo.tests.common import new_test_user


@tagged("post_install", "-at_install")
class TestSaleOrderLineDescriptionUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.config.settings"].create(
            {"group_use_product_description_per_so_line": True}
        ).execute()
        cls.tour_user = new_test_user(
            cls.env,
            login="sol_description_tour_user",
            groups="sales_team.group_sale_manager,account.group_account_invoice",
            context={"no_reset_password": True, "mail_create_nosubscribe": True},
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "description_sale": "Sale description for test product",
            }
        )
        cls.sale_order = (
            cls.env["sale.order"]
            .with_user(cls.tour_user)
            .create(
                {
                    "partner_id": cls.partner.id,
                    "order_line": [Command.create({"product_id": cls.product.id})],
                }
            )
        )

    def test_manual_description_edit_keeps_product_name_hidden_tour(self):
        self.assertEqual(self.sale_order.order_line.name, self.product.description_sale)

        self.start_tour(
            f"/odoo/sales/{self.sale_order.id}",
            "sale_order_line_description_manual_edit",
            login="sol_description_tour_user",
        )

        self.sale_order.order_line.invalidate_recordset(["name"])
        self.assertEqual(
            self.sale_order.order_line.name,
            f"{self.product.description_sale} test",
        )
