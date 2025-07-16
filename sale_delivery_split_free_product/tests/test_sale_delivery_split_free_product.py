# Copyright 2025 Moduon Team S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestSaleDeliverySplitFreeProduct(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Only 1 step for simplification
        cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.user.id)], limit=1
        ).write({"delivery_steps": "ship_only"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

    def test_procurement_split_product(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": "Test Product",
                            "price_unit": 1.0,
                            "product_uom_qty": 1,
                            "discount": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": "Test Free Product",
                            "price_unit": 1.0,
                            "product_uom_qty": 1,
                            "discount": 100.0,
                        },
                    ),
                ],
            }
        )
        sale.action_confirm()
        # Ensure two pickings are created, one for the paid product and one for the free product
        self.assertEqual(
            len(sale.picking_ids), 2, "There should be two pickings created."
        )
        # Remove the free product line
        sale.order_line.filtered(lambda line: line.discount == 100.0).write(
            {"product_uom_qty": 0.0}
        )
        # Check picking for the free product is cancelled
        cancelled_picking = sale.picking_ids.filtered_domain([("state", "=", "cancel")])
        self.assertEqual(
            len(cancelled_picking), 1, "There should be one picking cancelled."
        )
        # Ensure cancelled picking has "/FREE" text in its procurement group
        self.assertIn("/FREE", cancelled_picking.group_id.name)
