# Copyright 2026 Juan Carlos Oñate - Tecnativa <juancarlos.onate@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderPartnerRestrict(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_ok = cls.env["res.partner"].create(
            {
                "name": "OK Partner",
                "email": "ok@test.com",
            }
        )
        cls.product = cls.env.ref("product.product_product_6")

    def test_order_ok_partner_not_canceled(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_ok.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertNotEqual(order.state, "cancel")

    def test_order_blocked_by_email_rule(self):
        self.env["sale.order.block.rule"].create(
            {
                "name": "Block Spam Emails",
                "partner_field": "email",
                "blocked_values": "spam@test.com, blocked@test.com",
                "block_message": "Spam email detected",
            }
        )
        partner_spam = self.env["res.partner"].create(
            {
                "name": "Spam Partner",
                "email": "spam@test.com",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": partner_spam.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order.state, "cancel")
        self.assertTrue(
            any("Block Rule Triggered" in msg.body for msg in order.message_ids)
        )

    def test_order_blocked_by_zip_rule(self):
        self.env["sale.order.block.rule"].create(
            {
                "name": "Block Invalid ZIP",
                "partner_field": "zip",
                "blocked_values": "00000, 99999",
                "block_message": "Invalid ZIP code",
            }
        )
        partner_invalid_zip = self.env["res.partner"].create(
            {
                "name": "Invalid ZIP Partner",
                "zip": "00000",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": partner_invalid_zip.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order.state, "cancel")
        self.assertTrue(
            any("Invalid ZIP code" in msg.body for msg in order.message_ids)
        )

    def test_order_not_blocked_by_inactive_rule(self):
        self.env["sale.order.block.rule"].create(
            {
                "name": "Inactive Rule",
                "partner_field": "email",
                "blocked_values": "ok@test.com",
                "block_message": "Should not block",
                "active": False,
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_ok.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertNotEqual(order.state, "cancel")

    def test_order_blocked_by_zip_range(self):
        spain = self.env.ref("base.es")
        self.env["sale.order.block.rule"].create(
            {
                "name": "Block Canary Islands ZIP Range",
                "partner_field": "zip",
                "country_id": spain.id,
                "zip_range_from": "35001",
                "zip_range_to": "35999",
                "block_message": "Canary Islands ZIP range blocked",
            }
        )
        partner_in_range = self.env["res.partner"].create(
            {
                "name": "Partner in Range",
                "zip": "35500",
                "country_id": spain.id,
            }
        )
        partner_out_range = self.env["res.partner"].create(
            {
                "name": "Partner out of Range",
                "zip": "28001",
                "country_id": spain.id,
            }
        )
        order_in_range = self.env["sale.order"].create(
            {
                "partner_id": partner_in_range.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        order_out_range = self.env["sale.order"].create(
            {
                "partner_id": partner_out_range.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order_in_range.state, "cancel")
        self.assertNotEqual(order_out_range.state, "cancel")

    def test_order_blocked_by_shipping_partner(self):
        self.env["sale.order.block.rule"].create(
            {
                "name": "Block Spam Shipping Email",
                "partner_field": "email",
                "blocked_values": "spam@test.com",
                "block_message": "Spam shipping email",
            }
        )
        shipping_spam = self.env["res.partner"].create(
            {
                "name": "Shipping Spam",
                "type": "delivery",
                "parent_id": self.partner_ok.id,
                "email": "spam@test.com",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_ok.id,
                "partner_shipping_id": shipping_spam.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order.state, "cancel")
        self.assertTrue(
            any("Spam shipping email" in msg.body for msg in order.message_ids)
        )

    def test_order_blocked_by_invoice_partner(self):
        self.env["sale.order.block.rule"].create(
            {
                "name": "Block Invoice Phone",
                "partner_field": "phone",
                "blocked_values": "+34999999999",
                "block_message": "Phone blocked",
            }
        )
        invoice_blocked = self.env["res.partner"].create(
            {
                "name": "Blocked Invoice",
                "type": "invoice",
                "parent_id": self.partner_ok.id,
                "phone": "+34999999999",
            }
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_ok.id,
                "partner_invoice_id": invoice_blocked.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order.state, "cancel")
        self.assertTrue(any("Phone blocked" in msg.body for msg in order.message_ids))

    def test_order_blocked_by_zip_and_country(self):
        spain = self.env.ref("base.es")
        france = self.env.ref("base.fr")
        self.env["sale.order.block.rule"].create(
            {
                "name": "Block ZIP for Spain only",
                "partner_field": "zip",
                "blocked_values": "35001, 35002",
                "country_id": spain.id,
                "block_message": "ZIP blocked for Spain",
            }
        )
        partner_spain = self.env["res.partner"].create(
            {
                "name": "Spanish Partner",
                "zip": "35001",
                "country_id": spain.id,
            }
        )
        partner_france = self.env["res.partner"].create(
            {
                "name": "French Partner",
                "zip": "35001",
                "country_id": france.id,
            }
        )
        order_spain = self.env["sale.order"].create(
            {
                "partner_id": partner_spain.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        order_france = self.env["sale.order"].create(
            {
                "partner_id": partner_france.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        self.assertEqual(order_spain.state, "cancel")
        self.assertNotEqual(order_france.state, "cancel")
