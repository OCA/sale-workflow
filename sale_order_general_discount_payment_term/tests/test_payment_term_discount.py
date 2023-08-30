# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleOrderLineInput(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_term = cls.env.ref("account.account_payment_term_15days")
        cls.payment_term.sale_discount = 10
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "Contact Test",
                "parent_id": cls.partner.id,
                "type": "contact",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "payment_term_id": cls.payment_term.id,
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
            }
        )
        cls.View = cls.env["ir.ui.view"]

    def test_default_partner_discount(self):
        self.assertEqual(self.order.general_discount, 10)
        self.assertEqual(self.order.amount_untaxed, 900)
