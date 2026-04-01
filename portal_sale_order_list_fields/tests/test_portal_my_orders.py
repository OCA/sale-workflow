# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install", "pruebas")
class TestPortalMyOrders(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal User Test",
                "login": "portal_user_test",
                "password": "portal_password",
                "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )
        cls.portal_partner = cls.portal_user.partner_id

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "type": "consu",
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.portal_partner.id,
                "client_order_ref": "REF-CLIENT-999",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

        cls.sale_order.action_confirm()

    def test_portal_my_orders_custom_fields(self):
        self.authenticate("portal_user_test", "portal_password")

        response = self.url_open("/my/orders")

        self.assertEqual(response.status_code, 200)

        self.assertIn("Client Order Ref.", response.text)
        self.assertIn("Amount Untaxed", response.text)

        self.assertIn("REF-CLIENT-999", response.text)

        self.assertIn("200", response.text)
