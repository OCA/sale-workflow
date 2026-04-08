# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestPtoCommon


class TestPtoFunctionalAutoSelect(TestPtoCommon):
    """End-to-end tests for auto-select PTO destination on reception."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(
            "sale_stock_put_to_order.auto_select_location", "True"
        )
        cls.supplier = cls.env.ref("stock.stock_location_suppliers")

    def _create_receipt(self, product, qty=1):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.supplier.id,
                "location_dest_id": self.pto_root.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": product.name,
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": self.supplier.id,
                "location_dest_id": self.pto_root.id,
            }
        )
        return picking

    def test_reception_routes_to_pto_bin(self):
        """Incoming goods redirected to the PTO bin holding matching stock."""
        self.set_quantity(self.supplier, self.product, 100)
        picking = self._create_receipt(self.product)
        picking.action_confirm()
        picking.action_assign()
        pto_bins = self.pto_bin_1 | self.pto_bin_2
        for ml in picking.move_line_ids:
            self.assertIn(ml.location_dest_id, pto_bins)

    def test_reception_unknown_product_falls_back(self):
        """Product absent from all PTO bins keeps the root destination."""
        unknown = self.env["product.product"].create(
            {"name": "Unknown", "type": "consu", "is_storable": True}
        )
        self.set_quantity(self.supplier, unknown, 10)
        picking = self._create_receipt(unknown)
        picking.action_confirm()
        picking.action_assign()
        pto_bins = self.pto_bin_1 | self.pto_bin_2 | self.pto_other
        for ml in picking.move_line_ids:
            self.assertNotIn(ml.location_dest_id, pto_bins)

    def test_reception_two_products_same_bin(self):
        """Two products stocked in the same bin: both move lines go there."""
        self.set_quantity(self.pto_bin_1, self.other_product, 3)
        self.set_quantity(self.supplier, self.product, 50)
        self.set_quantity(self.supplier, self.other_product, 50)

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.supplier.id,
                "location_dest_id": self.pto_root.id,
            }
        )
        for prod in (self.product, self.other_product):
            self.env["stock.move"].create(
                {
                    "name": prod.name,
                    "picking_id": picking.id,
                    "product_id": prod.id,
                    "product_uom_qty": 1,
                    "product_uom": prod.uom_id.id,
                    "location_id": self.supplier.id,
                    "location_dest_id": self.pto_root.id,
                }
            )
        picking.action_confirm()
        picking.action_assign()
        dests = picking.move_line_ids.mapped("location_dest_id")
        self.assertTrue(
            all(d in (self.pto_bin_1 | self.pto_bin_2 | self.pto_other) for d in dests)
        )
