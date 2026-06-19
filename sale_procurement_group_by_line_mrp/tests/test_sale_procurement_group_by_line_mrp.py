# Copyright 2026 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestSaleProcurementGroupByLineMrp(TransactionCase):
    """Regression test for double procurement on nested kit products"""

    def setUp(self):
        super().setUp()
        self.sale_model = self.env["sale.order"]
        self.order_line_model = self.env["sale.order.line"]
        self.product_model = self.env["product.product"]
        self.product_ctg = self.env["product.category"].create({"name": "test_kit_ctg"})
        self.customer = self.env.ref("base.res_partner_2")
        self.warehouse = self.env.ref("stock.warehouse0")

    def _create_product(self, name):
        return self.product_model.create(
            {
                "name": name,
                "categ_id": self.product_ctg.id,
                "type": "product",
            }
        )

    def _create_kit(self, name, components):
        """Create a storable product with a phantom (kit) BoM."""
        kit = self._create_product(name)
        self.env["mrp.bom"].create(
            {
                "product_id": kit.id,
                "product_tmpl_id": kit.product_tmpl_id.id,
                "type": "phantom",
                "bom_line_ids": [
                    (0, 0, {"product_id": comp.id, "product_qty": 1.0})
                    for comp in components
                ],
            }
        )
        return kit

    def test_nested_kit_no_double_procurement(self):
        """Confirming a SO with a nested kit should produce exactly one stock
        move per leaf component
        """
        leaf1 = self._create_product("leaf_component_1")
        leaf2 = self._create_product("leaf_component_2")
        inner_kit = self._create_kit("inner_kit", [leaf1, leaf2])
        plain = self._create_product("plain_component")
        outer_kit = self._create_kit("outer_kit", [plain, inner_kit])
        sale = self.sale_model.create(
            {
                "partner_id": self.customer.id,
                "warehouse_id": self.warehouse.id,
                "picking_policy": "direct",
            }
        )
        self.order_line_model.create(
            {
                "order_id": sale.id,
                "product_id": outer_kit.id,
                "product_uom_qty": 1.0,
                "name": "Nested kit sale line",
            }
        )
        sale.action_confirm()
        all_moves = sale.picking_ids.mapped("move_lines")
        # Without fix: 6 moves (plain + leaf1 + leaf2 each procured twice)
        # With fix: 3 moves (plain + leaf1 + leaf2 each procured once)
        self.assertEqual(len(all_moves), 3)
        for move in all_moves:
            self.assertEqual(move.product_uom_qty, 1.0)
