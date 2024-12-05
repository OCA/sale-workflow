# Copyright 2020-22 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestStockSourcingAddressCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.product_model = cls.env["product.product"]
        cls.move_model = cls.env["stock.move"]
        cls.location_model = cls.env["stock.location"]

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customer_loc_default = cls.env.ref("stock.stock_location_customers")
        cls.customer_loc_secondary = cls.location_model.create(
            {"name": "Test customer location", "usage": "customer"}
        )
        cls.partner = cls.partner_model.create({"name": "Test partner"})
        cls.address_1 = cls.partner_model.create(
            {"name": "Address 1", "parent_id": cls.partner.id, "type": "delivery"}
        )
        cls.address_2 = cls.partner_model.create(
            {"name": "Address 2", "parent_id": cls.partner.id, "type": "delivery"}
        )
        cls.product = cls.product_model.create(
            {"name": "Test product", "is_storable": True}
        )

        # Create route for secondary customer location:
        cls.secondary_route = cls.env["stock.route"].create(
            {
                "warehouse_selectable": True,
                "name": "Ship to customer sec location",
                "warehouse_ids": [(6, 0, cls.warehouse.ids)],
            }
        )
        cls.wh2_rule = cls.env["stock.rule"].create(
            {
                "location_dest_id": cls.customer_loc_secondary.id,
                "location_src_id": cls.warehouse.lot_stock_id.id,
                "action": "pull_push",
                "location_dest_from_rule": True,
                "warehouse_id": cls.warehouse.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "name": "Stock -> Customers 2",
                "route_id": cls.secondary_route.id,
            }
        )

        # Create a SO with a couple of lines:
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": cls.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": cls.product.list_price,
                        },
                    ),
                ],
            }
        )
        cls.line_1 = cls.so.order_line[0]
        cls.line_2 = cls.so.order_line[1]
