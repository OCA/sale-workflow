# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrderLineSection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Section Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Section Product",
                "type": "service",
            }
        )

    def _create_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {"name": "S1", "display_type": "line_section", "sequence": 10},
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "L1",
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom_id": self.product.uom_id.id,
                            "price_unit": 100.0,
                            "sequence": 20,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "L2",
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom_id": self.product.uom_id.id,
                            "price_unit": 100.0,
                            "sequence": 30,
                        },
                    ),
                    (
                        0,
                        0,
                        {"name": "S2", "display_type": "line_section", "sequence": 40},
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "L3",
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom_id": self.product.uom_id.id,
                            "price_unit": 100.0,
                            "sequence": 50,
                        },
                    ),
                ],
            }
        )

    def test_section_id_computed_from_previous_section(self):
        order = self._create_order()
        s1 = order.order_line.filtered(lambda line: line.name == "S1")
        s2 = order.order_line.filtered(lambda line: line.name == "S2")
        l1 = order.order_line.filtered(lambda line: line.name == "L1")
        l2 = order.order_line.filtered(lambda line: line.name == "L2")
        l3 = order.order_line.filtered(lambda line: line.name == "L3")

        self.assertFalse(s1.section_id)
        self.assertFalse(s2.section_id)
        self.assertEqual(l1.section_id, s1)
        self.assertEqual(l2.section_id, s1)
        self.assertEqual(l3.section_id, s2)

    def test_section_id_recomputed_when_section_sequence_changes(self):
        order = self._create_order()
        s1 = order.order_line.filtered(lambda line: line.name == "S1")
        s2 = order.order_line.filtered(lambda line: line.name == "S2")
        l1 = order.order_line.filtered(lambda line: line.name == "L1")
        l2 = order.order_line.filtered(lambda line: line.name == "L2")
        l3 = order.order_line.filtered(lambda line: line.name == "L3")

        s2.write({"sequence": 25})

        self.assertEqual(l1.section_id, s1)
        self.assertEqual(l2.section_id, s2)
        self.assertEqual(l3.section_id, s2)
