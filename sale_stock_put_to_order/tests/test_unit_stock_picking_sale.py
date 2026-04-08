# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestSalePtoCommon


class TestStockPickingSale(TestSalePtoCommon):
    """Tests for sale-order-aware put-to-order resolution on stock.picking."""

    def test_get_pto_source_products_from_sale_order(self):
        """Products sourced from the linked sale order."""
        products = self.picking._get_pto_source_products()
        self.assertEqual(products, self.product)

    def test_get_pto_source_products_multi_product_so(self):
        """All SO products returned including lines not yet on picking."""
        extra_product = self.env["product.product"].create(
            {"name": "Product C", "type": "consu", "is_storable": True}
        )
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": extra_product.name,
                "product_id": extra_product.id,
                "product_uom_qty": 2,
                "product_uom": extra_product.uom_id.id,
                "price_unit": 50,
            }
        )
        products = self.picking._get_pto_source_products()
        self.assertIn(self.product, products)
        self.assertIn(extra_product, products)

    def test_get_pto_source_products_fallback_no_sale(self):
        """Fallback to move products when no sale order is linked."""
        self.picking.move_ids.write({"sale_line_id": False})
        products = self.picking._get_pto_source_products()
        self.assertIn(self.product, products)

    def test_get_pto_source_products_via_group_id(self):
        """SO found via procurement group when sale_line_id is missing.

        Internal transfers (e.g. Dispatch → PTO) share the procurement
        group with the originating SO but don't carry sale_line_id.
        """
        self.sale_order.action_confirm()
        self.picking.move_ids.write({"sale_line_id": False})
        self.picking.group_id = self.sale_order.procurement_group_id
        products = self.picking._get_pto_source_products()
        self.assertIn(self.product, products)

    def test_find_pto_dest_location_via_sale_order(self):
        """Destination resolution uses full SO product scope."""
        extra_product = self.env["product.product"].create(
            {"name": "Product D", "type": "consu", "is_storable": True}
        )
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": extra_product.name,
                "product_id": extra_product.id,
                "product_uom_qty": 1,
                "product_uom": extra_product.uom_id.id,
                "price_unit": 75,
            }
        )
        self.set_quantity(self.pto_other, extra_product, 5)
        self.reset_quantity(self.pto_bin_2, self.product)
        self.reset_quantity(self.pto_other, self.other_product)

        dest = next(
            (
                loc
                for loc, _ in self.picking._find_pto_dest_location_and_quants(
                    excluded_locations=self.pto_bin_1,
                )
            ),
            self.env["stock.location"],
        )
        self.assertEqual(dest, self.pto_other)
