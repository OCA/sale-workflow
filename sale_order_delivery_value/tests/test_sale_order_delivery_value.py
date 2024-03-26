from odoo.tests import Form, tagged

from odoo.addons.sale.tests.test_sale_product_attribute_value_config import (
    TestSaleProductAttributeValueCommon,
)


@tagged("post_install", "-at_install")
class TestSaleOrderDeliveryValue(TestSaleProductAttributeValueCommon):
    def setUp(self):
        super(TestSaleProductAttributeValueCommon, self).setUp()

        self.largeCabinet = self.env["product.product"].create(
            {
                "name": "Large Cabinet",
                "list_price": 320.0,
                "taxes_id": False,
            }
        )
        self.conferenceChair = self.env["product.product"].create(
            {
                "name": "Conference Chair",
                "list_price": 16.5,
                "taxes_id": False,
            }
        )

        self.drawerBlack = self.env["product.product"].create(
            {
                "name": "Drawer Black",
                "list_price": 25.0,
                "taxes_id": False,
            }
        )

        self.steve = self.env["res.partner"].create(
            {
                "name": "Steve Bucknor",
                "email": "steve.bucknor@example.com",
            }
        )
        self.empty_order = self.env["sale.order"].create({"partner_id": self.steve.id})
        self.tax_sale_10 = self.env["account.tax"].create(
            {"name": "Sale tax 10", "type_tax_use": "sale", "amount": "10.00"}
        )
        self.tax_sale_20 = self.env["account.tax"].create(
            {"name": "Sale tax 20", "type_tax_use": "sale", "amount": "20.00"}
        )

    def test_sale_order_delivery_value_discount(self):
        order = self.empty_order
        self.env["sale.order.line"].create(
            {
                "product_id": self.largeCabinet.id,
                "name": "Discounted Large Cabinet",
                "product_uom_qty": 1.0,
                "order_id": order.id,
                "discount": 50.0,
                "price_unit": 137.0,
            }
        )
        self.env["sale.order.line"].create(
            {
                "product_id": self.conferenceChair.id,
                "name": "Conference chair",
                "product_uom_qty": 4.0,
                "order_id": order.id,
                "price_unit": 42,
            }
        )

        self.assertAlmostEqual(order.amount_untaxed, 137 / 2 + 4 * 42)
        self.assertAlmostEqual(order.amount_tax, 0)
        self.assertAlmostEqual(order.amount_total, 137 / 2 + 4 * 42)
        self.assertAlmostEqual(order.amount_delivered_untaxed, 0)
        self.assertAlmostEqual(order.amount_delivered_tax, 0)
        self.assertAlmostEqual(order.amount_delivered_total, 0)
        self.assertAlmostEqual(order.amount_undelivered_untaxed, 137 / 2 + 4 * 42)
        self.assertAlmostEqual(order.amount_undelivered_tax, 0)
        self.assertAlmostEqual(order.amount_undelivered_total, 137 / 2 + 4 * 42)

        order.action_confirm()
        order.picking_ids.move_line_ids[0].qty_done = 1
        order.picking_ids.move_line_ids[1].qty_done = 2
        picking = order.picking_ids.ensure_one()
        res = picking.button_validate()
        # Create backorder
        Form(self.env[res["res_model"]].with_context(res["context"])).save().process()

        self.assertAlmostEqual(order.amount_untaxed, 137 / 2 + 4 * 42)
        self.assertAlmostEqual(order.amount_tax, 0)
        self.assertAlmostEqual(order.amount_total, 137 / 2 + 4 * 42)

        self.assertAlmostEqual(order.amount_delivered_untaxed, 137 / 2 + 2 * 42)
        self.assertAlmostEqual(order.amount_delivered_tax, 0)
        self.assertAlmostEqual(order.amount_delivered_total, 137 / 2 + 2 * 42)

        self.assertAlmostEqual(order.amount_undelivered_untaxed, 2 * 42)
        self.assertAlmostEqual(order.amount_undelivered_tax, 0)
        self.assertAlmostEqual(order.amount_undelivered_total, 2 * 42)

        backorder = order.picking_ids.filtered(
            lambda p: p.state == "assigned"
        ).ensure_one()
        backorder.move_line_ids[0].qty_done = 2
        self.assertAlmostEqual(backorder.button_validate(), True)

        self.assertAlmostEqual(order.amount_untaxed, 137 / 2 + 4 * 42)
        self.assertAlmostEqual(order.amount_tax, 0)
        self.assertAlmostEqual(order.amount_total, 137 / 2 + 4 * 42)
        self.assertAlmostEqual(order.amount_delivered_untaxed, 137 / 2 + 4 * 42)
        self.assertAlmostEqual(order.amount_delivered_tax, 0)
        self.assertAlmostEqual(order.amount_delivered_total, 137 / 2 + 4 * 42)

        self.assertAlmostEqual(order.amount_undelivered_untaxed, 0)
        self.assertAlmostEqual(order.amount_undelivered_tax, 0)
        self.assertAlmostEqual(order.amount_undelivered_total, 0)

    def test_sale_order_delivery_value_with_tax(self):
        order = self.empty_order
        self.env["sale.order.line"].create(
            {
                "product_id": self.largeCabinet.id,
                "name": "Discounted Large Cabinet",
                "product_uom_qty": 2.0,
                "order_id": order.id,
                "tax_id": self.tax_sale_10,
            }
        )
        self.env["sale.order.line"].create(
            {
                "product_id": self.conferenceChair.id,
                "name": "Conference chair",
                "product_uom_qty": 6.0,
                "order_id": order.id,
                "tax_id": self.tax_sale_20,
            }
        )
        self.env["sale.order.line"].create(
            {
                "product_id": self.drawerBlack.id,
                "name": "Drawer black",
                "product_uom_qty": 3.0,
                "order_id": order.id,
            }
        )

        self.assertAlmostEqual(order.amount_untaxed, 2 * 320 + 6 * 16.5 + 3 * 25)
        self.assertAlmostEqual(order.amount_tax, 2 * 320 * 0.1 + 6 * 16.5 * 0.2)
        self.assertAlmostEqual(
            order.amount_total, 2 * 320 * 1.1 + 6 * 16.5 * 1.2 + 3 * 25
        )
        self.assertAlmostEqual(order.amount_delivered_untaxed, 0)
        self.assertAlmostEqual(order.amount_delivered_tax, 0)
        self.assertAlmostEqual(order.amount_delivered_total, 0)
        self.assertAlmostEqual(
            order.amount_undelivered_untaxed, 2 * 320 + 6 * 16.5 + 3 * 25
        )
        self.assertAlmostEqual(
            order.amount_undelivered_tax, 2 * 320 * 0.1 + 6 * 16.5 * 0.2
        )
        self.assertAlmostEqual(
            order.amount_undelivered_total, 2 * 320 * 1.1 + 6 * 16.5 * 1.2 + 3 * 25
        )

        order.action_confirm()
        order.picking_ids.move_line_ids[0].qty_done = 1
        order.picking_ids.move_line_ids[1].qty_done = 3
        order.picking_ids.move_line_ids[2].qty_done = 2
        picking = order.picking_ids.ensure_one()
        res = picking.button_validate()
        # Create backorder
        Form(self.env[res["res_model"]].with_context(res["context"])).save().process()

        self.assertAlmostEqual(order.amount_untaxed, 2 * 320 + 6 * 16.5 + 3 * 25)
        self.assertAlmostEqual(order.amount_tax, 2 * 320 * 0.1 + 6 * 16.5 * 0.2)
        self.assertAlmostEqual(
            order.amount_total, 2 * 320 * 1.1 + 6 * 16.5 * 1.2 + 3 * 25
        )

        self.assertAlmostEqual(
            order.amount_delivered_untaxed, 1 * 320 + 3 * 16.5 + 2 * 25
        )
        self.assertAlmostEqual(
            order.amount_delivered_tax, 1 * 320 * 0.1 + 3 * 16.5 * 0.2
        )
        self.assertAlmostEqual(
            order.amount_delivered_total, 1 * 320 * 1.1 + 3 * 16.5 * 1.2 + 2 * 25
        )

        self.assertAlmostEqual(
            order.amount_undelivered_untaxed, 1 * 320 + 3 * 16.5 + 1 * 25
        )
        self.assertAlmostEqual(
            order.amount_undelivered_tax, 1 * 320 * 0.1 + 3 * 16.5 * 0.2
        )
        self.assertAlmostEqual(
            order.amount_undelivered_total, 1 * 320 * 1.1 + 3 * 16.5 * 1.2 + 1 * 25
        )

        backorder = order.picking_ids.filtered(
            lambda p: p.state == "assigned"
        ).ensure_one()
        backorder.move_line_ids[0].qty_done = 1
        backorder.move_line_ids[1].qty_done = 3
        backorder.move_line_ids[2].qty_done = 1

        self.assertAlmostEqual(backorder.button_validate(), True)

        self.assertAlmostEqual(order.amount_untaxed, 2 * 320 + 6 * 16.5 + 3 * 25)
        self.assertAlmostEqual(order.amount_tax, 2 * 320 * 0.1 + 6 * 16.5 * 0.2)
        self.assertAlmostEqual(
            order.amount_total, 2 * 320 * 1.1 + 6 * 16.5 * 1.2 + 3 * 25
        )

        self.assertAlmostEqual(
            order.amount_delivered_untaxed, 2 * 320 + 6 * 16.5 + 3 * 25
        )
        self.assertAlmostEqual(
            order.amount_delivered_tax, 2 * 320 * 0.1 + 6 * 16.5 * 0.2
        )
        self.assertAlmostEqual(
            order.amount_delivered_total, 2 * 320 * 1.1 + 6 * 16.5 * 1.2 + 3 * 25
        )

        self.assertAlmostEqual(order.amount_undelivered_untaxed, 0)
        self.assertAlmostEqual(order.amount_undelivered_tax, 0)
        self.assertAlmostEqual(order.amount_undelivered_total, 0)
