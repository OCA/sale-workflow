# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSaleProductCatalogExtendedSecondaryUnit(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Catalog partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Catalog product", "sale_ok": True}
        )
        cls.box = cls.env["product.secondary.unit"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "name": "Box",
                "factor": 2.0,
                "uom_id": cls.product.uom_id.id,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def test_new_line_in_product_secondary_unit(self):
        self.product.sale_secondary_uom_id = self.box
        vals = self.order._get_catalog_line_quantity_vals(self.product, 4)
        self.assertEqual(
            vals,
            {
                "secondary_uom_id": self.box.id,
                "secondary_uom_qty": 4,
                "product_uom_qty": 8.0,
            },
        )

    def test_new_line_without_secondary_unit(self):
        vals = self.order._get_catalog_line_quantity_vals(self.product, 4)
        self.assertEqual(vals, {"product_uom_qty": 4})

    def test_update_line_qty_in_line_secondary_unit(self):
        """Editing a line from its catalog card sets the quantity in the
        secondary unit the card shows."""
        line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "secondary_uom_id": self.box.id,
                "secondary_uom_qty": 1,
                "product_uom_qty": 2,
            }
        )
        self.authenticate("admin", "admin")
        self.make_jsonrpc_request(
            "/product/catalog/sale/update_line_qty",
            {"line_id": line.id, "quantity": 3},
        )
        self.assertEqual(line.secondary_uom_qty, 3)
        self.assertEqual(line.product_uom_qty, 6)
        data = line._get_product_catalog_lines_data()
        self.assertEqual(data["quantity"], 3)
