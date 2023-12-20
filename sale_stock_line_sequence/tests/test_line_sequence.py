# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrderLineSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderLineSequence, cls).setUpClass()
        cls.sale_order = cls.env["sale.order"]
        cls.sale_order_line = cls.env["sale.order.line"]
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_product_4")

    def test_sale_order_moves_line_sequence(self):
        """
        Verify that the sequence is correctly assigned to the move associated
        with the sale order line it references.
        """
        vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "name": self.product.name,
                        "product_uom_qty": 1.0,
                        "price_unit": self.product.lst_price,
                    },
                ),
                (
                    0,
                    0,
                    {"name": "Section 1", "display_type": "line_section"},
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "name": self.product.name,
                        "product_uom_qty": 5.0,
                        "price_unit": self.product.lst_price,
                    },
                ),
                (
                    0,
                    0,
                    {"name": "Note 1", "display_type": "line_note"},
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "name": self.product.name,
                        "product_uom_qty": 15.0,
                        "price_unit": self.product.lst_price,
                    },
                ),
            ],
        }
        so = self.sale_order.create(vals)
        so.action_confirm()

        moves = so.picking_ids[0].move_ids_without_package
        self.assertNotEqual(len(so.order_line), len(moves))

        for move in moves:
            self.assertEqual(move.sequence, move.sale_line_id.visible_sequence)

    def test_write_purchase_order_line(self):
        vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product.id,
                        "name": self.product.name,
                        "product_uom_qty": 1.0,
                        "price_unit": self.product.lst_price,
                    },
                ),
            ],
        }
        so = self.sale_order.create(vals)
        so.action_confirm()

        so.write(
            {
                "order_line": [
                    (0, 0, {"name": "Note 1", "display_type": "line_note"}),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "product_uom_qty": 5.0,
                            "price_unit": self.product.lst_price,
                        },
                    ),
                ]
            }
        )

        moves = so.picking_ids[0].move_ids_without_package
        for move in moves:
            self.assertEqual(move.sequence, move.sale_line_id.visible_sequence)
