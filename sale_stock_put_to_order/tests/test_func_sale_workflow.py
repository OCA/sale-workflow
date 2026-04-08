# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestSalePtoCommon


class TestPtoFunctionalSaleOrder(TestSalePtoCommon):
    """End-to-end tests: sale order → reception → PTO bin resolution."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env.ref("stock.stock_location_suppliers")

    def _create_receipt_for_sale(self, sale_order):
        """Create a reception picking linked to a sale order."""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.supplier.id,
                "location_dest_id": self.pto_root.id,
            }
        )
        for line in sale_order.order_line:
            self.env["stock.move"].create(
                {
                    "name": line.product_id.name,
                    "picking_id": picking.id,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.product_uom_qty,
                    "product_uom": line.product_uom.id,
                    "location_id": self.supplier.id,
                    "location_dest_id": self.pto_root.id,
                    "sale_line_id": line.id,
                }
            )
        return picking

    def test_bin_groups_from_sale_order(self):
        """Bin groups reflect the full SO product scope."""
        picking = self._create_receipt_for_sale(self.sale_order)
        bin_groups = picking._get_pto_bin_groups()
        self.assertIn(self.product.id, bin_groups)
        self.assertEqual(bin_groups[self.product.id]["name"], self.pto_bin_1.name)

    def test_bin_groups_multi_product_sale_order(self):
        """All SO products mapped to the bin that holds them."""
        self.set_quantity(self.pto_bin_1, self.other_product, 5)
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": self.other_product.name,
                "product_id": self.other_product.id,
                "product_uom_qty": 1,
                "product_uom": self.other_product.uom_id.id,
                "price_unit": 50,
            }
        )
        picking = self._create_receipt_for_sale(self.sale_order)
        bin_groups = picking._get_pto_bin_groups()
        self.assertIn(self.product.id, bin_groups)
        self.assertIn(self.other_product.id, bin_groups)
        self.assertEqual(
            bin_groups[self.product.id]["name"],
            bin_groups[self.other_product.id]["name"],
        )

    def test_auto_select_with_sale_order(self):
        """Auto-select routes reception to PTO bin using SO product scope."""
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_stock_put_to_order.auto_select_location", "True"
        )
        self.set_quantity(self.supplier, self.product, 100)
        picking = self._create_receipt_for_sale(self.sale_order)
        picking.action_confirm()
        picking.action_assign()
        pto_bins = self.pto_bin_1 | self.pto_bin_2
        for ml in picking.move_line_ids:
            self.assertIn(ml.location_dest_id, pto_bins)

    def test_no_bin_group_when_pto_disabled(self):
        """No bin groups returned when PTO flag is cleared."""
        self.pto_root.is_pto = False
        picking = self._create_receipt_for_sale(self.sale_order)
        bin_groups = picking._get_pto_bin_groups()
        self.assertEqual(bin_groups, {})
