# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSaleFixedDiscountPortal(HttpCase):
    def test_portal_discounted_unit_prices(self):
        product = self.env["product.product"].create(
            {"name": "Test product", "type": "consu", "taxes_id": False}
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.env["res.partner"].create({"name": "Test"}).id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "price_unit": 100.0,
                            "discount": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": 3,
                            "price_unit": 50.0,
                            "discount_fixed": 5.0,
                        }
                    ),
                ],
            }
        )
        response = self.url_open(order.get_portal_url())
        self.assertEqual(response.status_code, 200)
        # discounted unit prices, next to the struck-through 100.00 and 50.00
        self.assertIn("90.00", response.text)
        self.assertIn("45.00", response.text)
