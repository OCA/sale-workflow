# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPtoCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.product = cls.env["product.product"].create(
            {"name": "Product A", "type": "consu", "is_storable": True}
        )
        cls.other_product = cls.env["product.product"].create(
            {"name": "Product B", "type": "consu", "is_storable": True}
        )
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.picking_type = cls.warehouse.in_type_id
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.pto_root = cls.env["stock.location"].create(
            {"name": "PTO Root", "usage": "internal"}
        )
        cls.pto_bin_1 = cls.env["stock.location"].create(
            {
                "name": "PTO Bin 1",
                "usage": "internal",
                "location_id": cls.pto_root.id,
            }
        )
        cls.pto_bin_2 = cls.env["stock.location"].create(
            {
                "name": "PTO Bin 2",
                "usage": "internal",
                "location_id": cls.pto_root.id,
            }
        )
        cls.pto_other = cls.env["stock.location"].create(
            {
                "name": "PTO Other",
                "usage": "internal",
                "location_id": cls.pto_root.id,
            }
        )

        cls.pto_root.is_pto = True
        cls.picking_type.default_location_dest_id = cls.pto_root

        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.pto_bin_1.id,
                "location_dest_id": cls.stock_location.id,
            }
        )

        cls.env["stock.move"].create(
            {
                "name": "PTO Move",
                "picking_id": cls.picking.id,
                "product_id": cls.product.id,
                "product_uom_qty": 1,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.pto_bin_1.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.set_quantity(cls.pto_bin_1, cls.product, 10)
        cls.set_quantity(cls.pto_bin_2, cls.product, 1)
        cls.set_quantity(cls.pto_other, cls.other_product, 1)

    @classmethod
    def reset_quantity(cls, locations, products):
        cls.env["stock.quant"].search(
            [("location_id", "in", locations.ids), ("product_id", "in", products.ids)]
        ).unlink()

    @classmethod
    def set_quantity(cls, location, product, quantity):
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)


class TestSalePtoCommon(TestPtoCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Customer"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": fields.Datetime.now(),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        cls.sale_line = cls.sale_order.order_line[0]
        cls.picking.move_ids.write({"sale_line_id": cls.sale_line.id})
