# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Pierre Faniel - Niboo SPRL (<https://www.niboo.be/>)
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.sale_order_type.tests import test_sale_order_type


class TestSaleOrderType(test_sale_order_type.TestSaleOrderType):
    def setUp(self):
        super().setUp()
        self.warehouse = self.env["stock.warehouse"].create(
            {"name": "Warehouse Test", "code": "WT"}
        )
        self.product.invoice_policy = "order"
        self.free_carrier = self.env.ref("account.incoterm_FCA")
        self.sale_type.warehouse_id = self.warehouse
        self.sale_type.picking_policy = "one"
        self.sale_type.incoterm = self.free_carrier
        self.sale_type_quot.warehouse_id = self.warehouse
        self.sale_type_quot.picking_policy = "one"
        self.sale_route = self.env["stock.location.route"].create(
            {
                "name": "SO -> Customer",
                "product_selectable": True,
                "sale_selectable": True,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "SO -> Customer",
                            "action": "pull",
                            "picking_type_id": self.ref("stock.picking_type_in"),
                            "location_src_id": self.ref(
                                "stock.stock_location_components"
                            ),
                            "location_id": self.ref("stock.stock_location_customers"),
                        },
                    )
                ],
            }
        )
        self.sale_type_route = self.sale_type_model.create(
            {
                "name": "Test Sale Order Type-1",
                "sequence_id": self.sequence.id,
                "journal_id": self.journal.id,
                "warehouse_id": self.warehouse.id,
                "picking_policy": "one",
                "payment_term_id": self.immediate_payment.id,
                "pricelist_id": self.sale_pricelist.id,
                "incoterm_id": self.free_carrier.id,
                "route_id": self.sale_route.id,
            }
        )

    def test_sale_order_flow(self):
        sale_type = self.sale_type
        order = self.create_sale_order()
        self.assertEqual(order.type_id, sale_type)
        order.onchange_type_id()
        self.assertEqual(order.warehouse_id, sale_type.warehouse_id)
        self.assertEqual(order.picking_policy, sale_type.picking_policy)
        self.assertEqual(order.payment_term_id, sale_type.payment_term_id)
        self.assertEqual(order.pricelist_id, sale_type.pricelist_id)
        self.assertEqual(order.incoterm, sale_type.incoterm_id)
        order.action_confirm()
        invoice = order._create_invoices()
        self.assertEqual(invoice.sale_type_id, sale_type)
        self.assertEqual(invoice.journal_id, sale_type.journal_id)

    def test_sale_order_flow_route(self):
        order = self.create_sale_order()
        order.type_id = self.sale_type_route.id
        order.onchange_type_id()
        self.assertEqual(order.type_id.route_id, order.order_line[0].route_id)
        sale_line_dict = {
            "product_id": self.product.id,
            "name": self.product.name,
            "product_uom_qty": 2.0,
            "price_unit": self.product.lst_price,
        }
        order.write({"order_line": [(0, 0, sale_line_dict)]})
        order.onchange_type_id()
        self.assertEqual(order.type_id.route_id, order.order_line[1].route_id)
