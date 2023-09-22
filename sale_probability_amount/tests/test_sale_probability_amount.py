# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleProbabilityAmount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        cls.order = cls.env["sale.order"].create(
            {
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
                            "price_unit": 100.00,
                        },
                    )
                ],
            }
        )

    def test_default_value(self):
        self.assertEqual(self.order.probability, 50)

    def test_sale_confirm(self):
        self.order.action_confirm()
        self.assertEqual(self.order.probability, 100)

    def test_sale_cancel(self):
        self.order.action_cancel()
        self.assertEqual(self.order.probability, 0)

    def test_sale_draft(self):
        self.order.action_draft()
        self.assertEqual(self.order.probability, 50)
