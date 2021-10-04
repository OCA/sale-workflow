# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


class CommonPurchaseAmendment:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_obj = cls.env["stock.move"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env.ref("product.product_product_4")
        cls.product_2 = cls.env.ref("product.product_product_5")
        cls.product_service = cls.env.ref("product.product_product_1")
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.loc_stock = cls.env.ref("stock.stock_location_stock")
        cls.qty_wizard = cls.env["stock.change.product.qty"]

        vals = {
            "name": cls.env.ref("base.res_partner_2").id,
            "price": 500.0,
            "product_tmpl_id": cls.product.product_tmpl_id.id,
        }
        cls.env["product.supplierinfo"].create(vals)
        vals = {
            "name": "DROP SHIPPING",
            "sequence_id": cls.env.ref("stock.seq_picking_internal").id,
            "code": "outgoing",
            "warehouse_id": cls.warehouse.id,
            "sequence_code": "DROP",
            "default_location_src_id": cls.loc_supplier.id,
            "default_location_dest_id": cls.loc_customer.id,
        }
        pick_type_drop_shipping = cls.env["stock.picking.type"].create(vals)

        vals = {
            "name": "DROP SHIP",
            "sequence": 1,
            "sale_selectable": True,
            "rule_ids": [
                (
                    0,
                    0,
                    {
                        "name": "OUTPUT => Customers",
                        "action": "pull",
                        "location_src_id": cls.loc_supplier.id,
                        "location_id": cls.loc_customer.id,
                        "picking_type_id": pick_type_drop_shipping.id,
                        "procure_method": "make_to_stock",
                    },
                )
            ],
        }
        cls.route_drop = cls.env["stock.location.route"].create(vals)
        qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product_2.id,
                "product_tmpl_id": cls.product_2.product_tmpl_id.id,
                "new_quantity": 1.0,
            }
        )
        qty_wizard.change_product_qty()

    @classmethod
    def _change_product_qty(cls, qty=1.0, product=None):
        if product is None:
            product = cls.product
        qty_wizard = cls.qty_wizard.create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": qty,
            }
        )
        qty_wizard.change_product_qty()

    @classmethod
    def _create_sale_order(cls):
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 2.0,
                            "route_id": cls.warehouse.mto_pull_id.route_id.id,
                        },
                    )
                ],
            }
        )
