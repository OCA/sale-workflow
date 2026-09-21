# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleOrderWarnMessage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        cls.warn_msg_parent = "This customer has a warn from parent"
        cls.parent = cls.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "sale_warn_msg": cls.warn_msg_parent,
            }
        )
        cls.warn_msg = "This customer has a warn"
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "sale_warn_msg": cls.warn_msg,
            }
        )

    def test_compute_sale_warn_msg(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 42,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(sale.sale_warn_msg, self.warn_msg)
        sale.action_confirm()
        self.assertFalse(sale.sale_warn_msg)

    def test_compute_sale_warn_msg_parent(self):
        self.partner.update({"parent_id": self.parent.id})
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 42,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(
            sale.sale_warn_msg, self.warn_msg_parent + "\n" + self.warn_msg
        )

    def test_partner_without_warn_msg(self):
        # set partner not to have warning
        self.partner.update({"parent_id": None, "sale_warn_msg": False})

        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 42,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(sale.sale_warn_msg, False)
