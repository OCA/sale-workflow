# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import TransactionCase


class TestSalePartnerDelay(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "sale_delay": 5,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "sale_delay": 3,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

    def test_partner_delay_added_to_product_delay(self):
        """Partner delay should be added to product delay"""
        self.assertEqual(self.order.order_line.customer_lead, 8.0)  # 5 + 3

    def test_partner_delay_zero_delay(self):
        """Partner without delay should not affect product delay"""
        self.partner.sale_delay = 0
        # First, assert that changing the partner's delay doesn't immediately
        # recompute the line's delay.
        self.assertEqual(self.order.order_line.customer_lead, 8.0)
        # Force the recomputation of the line's delay.
        self.order.modified(["partner_id"])
        self.assertEqual(self.order.order_line.customer_lead, 5.0)  # Only product delay

    def test_partner_delay_commercial_field(self):
        """Contact should inherit parent company's delay"""
        contact = self.env["res.partner"].create(
            {
                "name": "Contact",
                "parent_id": self.partner.id,
                "type": "contact",
            }
        )
        self.assertEqual(contact.sale_delay, 3)

    def test_partner_change_recomputes_lead(self):
        """Changing partner should recompute customer lead"""
        partner2 = self.env["res.partner"].create(
            {
                "name": "Partner 2",
                "sale_delay": 7,
            }
        )
        self.order.partner_id = partner2
        self.assertEqual(self.order.order_line.customer_lead, 12.0)  # 5 + 7

    def test_product_change_recomputes_lead(self):
        """Changing product should recompute customer lead"""
        product2 = self.env["product.product"].create(
            {
                "name": "Product 2",
                "sale_delay": 10,
            }
        )
        self.order.order_line.product_id = product2
        self.assertEqual(self.order.order_line.customer_lead, 13.0)  # 10 + 3
