# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleOrderLineUpdateRoute(SavepointCase):
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

        vals = {
            "name": cls.env.ref("base.res_partner_2").id,
            "price": 500.0,
            "product_tmpl_id": cls.product.product_tmpl_id.id,
        }
        cls.env["product.supplierinfo"].create(vals)

    def test_purchase_mto(self):
        """
        Create and confirm a sale order with MTO route
        The created move will use the default route Stock > Customers
        and purchase order

        Launch the wizard to update the route and select the drop shipping
        route.

        A new move is created from Vendors > Customers
        """
        self.warehouse.mto_pull_id.active = True
        self.warehouse.mto_pull_id.route_id.active = True
        # Force a Purchase Order
        self.warehouse.mto_pull_id.procure_method = "make_to_order"
        # Add Buy to product
        self.product.route_ids |= self.warehouse.buy_pull_id.route_id
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "route_id": self.warehouse.mto_pull_id.route_id.id,
                        },
                    )
                ],
            }
        )
        self.sale_order.action_confirm()

        self.assertEqual(1, len(self.sale_order.order_line.chained_purchase_line_ids))
