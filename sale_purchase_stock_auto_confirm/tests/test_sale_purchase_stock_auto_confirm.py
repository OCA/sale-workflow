from odoo import Command
from odoo.tests import new_test_user
from odoo.tests.common import users

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseSaleStockAutoConfirm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_test_user(
            cls.env,
            login="sale_purchase_stock_auto_confirm_user",
            groups="sales_team.group_sale_salesman",
        )
        cls.mto_route = cls.env["stock.warehouse"]._find_or_create_global_route(
            "stock.route_warehouse0_mto", cls.env._("Replenish on Order (MTO)")
        )
        cls.mto_route.active = True
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.customer = cls.env["res.partner"].create({"name": "New Customer"})
        cls.vendor = cls.env["res.partner"].create({"name": "New Vendor"})
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set([cls.mto_route.id, cls.buy_route.id])],
                "seller_ids": [Command.create({"partner_id": cls.vendor.id})],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set([cls.mto_route.id, cls.buy_route.id])],
                "seller_ids": [Command.create({"partner_id": cls.vendor.id})],
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 1,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 2,
                        },
                    ),
                ],
            }
        )

    @users("sale_purchase_stock_auto_confirm_user")
    def test_purchase_auto_validation_with_mto(self):
        """Test that the purchase order is auto-validated when the sale order
        is confirmed for a product with MTO route
        """
        self.company.purchase_auto_validation = True
        self.sale_order.action_confirm()
        purchase = self.sale_order._get_purchase_orders()
        self.assertEqual(purchase.state, "purchase")
        self.assertEqual(len(purchase.order_line), 2)

    @users("sale_purchase_stock_auto_confirm_user")
    def test_purchase_no_auto_validation(self):
        """Test that the purchase order is not auto-validated when the sale order
        is confirmed for a product with MTO route
        """
        self.company.purchase_auto_validation = False
        self.sale_order.action_confirm()
        purchase = self.sale_order._get_purchase_orders()
        self.assertEqual(purchase.state, "draft")
        self.assertEqual(len(purchase.order_line), 2)
