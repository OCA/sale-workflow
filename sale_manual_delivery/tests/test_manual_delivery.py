# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError

from odoo.addons.sale.tests.test_sale_common import TestSale


class TestSaleStock(TestSale):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
        self.product_service = self.env.ref("product.product_product_1")
        self.product2 = self.env.ref("product.product_delivery_02")
        self.product3 = self.env.ref("product.product_order_01")
        self.carrier1 = self.env.ref("delivery.delivery_carrier")
        self.carrier2 = self.env.ref("delivery.normal_delivery_carrier")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 100
        )
        self.precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

    def _manual_delivery_wizard(self, records, vals=None):
        if not vals:
            vals = {}
        return (
            self.env["manual.delivery"]
            .with_context(active_model=records._name, active_ids=records.ids,)
            .create(vals)
        )

    def test_00_sale_manual_delivery(self):
        """
        Test SO's manual delivery
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product_service.name,
                            "product_id": self.product_service.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.product_service.uom_id.id,
                            "price_unit": self.product_service.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
            }
        )
        # confirm our standard so, check the picking
        order.action_confirm()
        self.assertFalse(
            order.picking_ids,
            'No picking should be created for "manual delivery" orders',
        )
        # open the manual delivery wizard
        action = order.action_manual_delivery_wizard()
        self.assertEqual(action["res_model"], "manual.delivery")
        # create a manual delivery for all ordered quantity
        self._manual_delivery_wizard(order).confirm()
        # check picking is created
        self.assertTrue(
            order.picking_ids,
            'Picking should be created after "manual delivery" wizard call',
        )
        # create a manual delivery, nothing left to ship
        wizard = self._manual_delivery_wizard(order)
        self.assertFalse(
            wizard.line_ids,
            "After picking creation for all products, "
            "no lines should be left in the wizard",
        )
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids), 1.0, "Picking number should remain 1.0"
        )
        sale_line_1 = order.order_line[0]
        sale_line_2 = order.order_line[1]
        self.assertNotAlmostEqual(sale_line_1.qty_procured, 0, self.precision)
        self.assertAlmostEqual(sale_line_2.qty_procured, 0, self.precision)

    def test_01_sale_standard_delivery(self):
        """
        Test SO's standard delivery
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": False,
            }
        )
        # confirm our standard so, check the picking
        order.action_confirm()
        self.assertTrue(
            order.picking_ids,
            'Picking should be created for "standard delivery" orders',
        )
        # deliver completely
        pick = order.picking_ids
        pick.action_assign()
        pick.move_line_ids.write({"qty_done": 5})
        pick.button_validate()
        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in order.order_line)
        self.assertEqual(del_qty, 5.0, "Delivery quantity doesn't match")

    def test_02_sale_various_manual_delivery(self):
        """
        Test SO's various manual delivery
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
            }
        )
        # confirm our standard so, check the picking
        order.action_confirm()
        self.assertFalse(
            order.picking_ids,
            'No picking should be created for "manual delivery" orders',
        )
        # create a manual delivery for part of ordered quantity
        wizard = self._manual_delivery_wizard(order)
        wizard.line_ids.write({"quantity": 2.0})
        wizard.confirm()
        # check picking is created
        self.assertEqual(
            len(order.picking_ids),
            1,
            'Picking should be created after "manual delivery" wizard call',
        )
        # deliver completely
        pick = order.picking_ids
        pick.action_assign()
        pick.move_line_ids.write({"qty_done": 2})
        pick.button_validate()
        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in order.order_line)
        self.assertEqual(del_qty, 2.0, "Delivery quantity doesn't match")
        # a manual delivery with qty 0 shouldn't do anything
        wizard = self._manual_delivery_wizard(order)
        wizard.line_ids.write({"quantity": 0.0})
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids), 1.0, "No picking should've been created",
        )
        # try to create a manual delivery with more quantity than the ordered
        wizard = self._manual_delivery_wizard(order)
        with self.assertRaises(UserError):
            wizard.line_ids.write({"quantity": 10.0})
            wizard.confirm()
        # create a manual delivery, 3.0 left to ship
        wizard = self._manual_delivery_wizard(order)
        wizard.line_ids.write({"quantity": 3.0})
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids), 2.0, "Picking number doesn't match",
        )

    def test_03_sale_selected_lines(self):
        """
        Test SO's various manual delivery
        """
        order1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
            }
        )
        order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product2.name,
                            "product_id": self.product2.id,
                            "product_uom_qty": 2.0,
                            "product_uom": self.product2.uom_id.id,
                            "price_unit": self.product2.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
            }
        )
        order3 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product3.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 3.0,
                            "product_uom": self.product3.uom_id.id,
                            "price_unit": self.product3.list_price,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
            }
        )
        # confirm our standard so, check the picking
        order1.action_confirm()
        order2.action_confirm()
        order3.action_confirm()
        some_lines = order1.order_line | order3.order_line
        all_lines = order1.order_line | order2.order_line | order3.order_line
        # create a manual delivery for part of ordered quantity
        wizard = self._manual_delivery_wizard(some_lines)
        self.assertEqual(sum(wizard.line_ids.mapped("quantity")), 4.0)
        wizard.confirm()
        # check picking is created
        self.assertTrue(
            order3.picking_ids,
            'Picking should be created after "manual delivery" wizard call',
        )
        self.assertEqual(
            len(order3.picking_ids.move_lines),
            1,
            "Different sales orders should still create different pickings",
        )
        self.assertFalse(
            order2.picking_ids,
            'Picking should not be created after "manual delivery" wizard call',
        )
        # test action undelivered
        undelivered = self.env["sale.order.line"].search(
            [
                ("qty_to_procure", ">", 0),
                ("state", "=", "sale"),
                ("id", "in", all_lines.ids),
            ]
        )
        self.assertEqual(
            undelivered, order2.order_line, "Bad pending qty to deliver filter",
        )

    def test_03_sale_multi_delivery(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product2, self.stock_location, 100
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product2.name,
                            "product_id": self.product2.id,
                            "product_uom_qty": 10.0,
                            "product_uom": self.product2.uom_id.id,
                            "price_unit": self.product2.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
            }
        )

        # confirm our standard so, check the picking
        order.action_confirm()
        self.assertFalse(
            order.picking_ids,
            'No picking should be created for "manual delivery" orders',
        )
        # create a manual delivery for part of ordered quantity
        date_now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        wizard = self._manual_delivery_wizard(
            order.order_line[0],
            {"carrier_id": order.carrier_id.id, "date_planned": date_now},
        )
        wizard.line_ids.write({"quantity": 2.0})
        wizard.confirm()
        # check picking is created
        self.assertEqual(
            len(order.picking_ids),
            1,
            'Picking should be created after "manual delivery" wizard call',
        )
        first_picking = order.picking_ids
        self.assertEqual(
            first_picking.scheduled_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            date_now,
        )
        # create a second manual delivery for next week
        date_next_week = date_now + relativedelta(weeks=1)
        wizard = self._manual_delivery_wizard(
            order.order_line[1],
            {"carrier_id": order.carrier_id.id, "date_planned": date_next_week},
        )
        wizard.line_ids.write({"quantity": 3.0})
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids),
            2,
            "Sale Manual Delivery: second picking should be created after"
            ' "manual delivery" wizard call with different date',
        )
        second_picking = order.picking_ids - first_picking
        self.assertEqual(
            second_picking.scheduled_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            date_next_week,
        )
        # create a third manual delivery for today (should be mixed with first)
        new_date_now = datetime.now()
        wizard = self._manual_delivery_wizard(
            order.order_line[0],
            {"carrier_id": order.carrier_id.id, "date_planned": new_date_now},
        )
        wizard.line_ids.write({"quantity": 5.0})
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids),
            2,
            "Sale Manual Delivery: new moves should be merged in first picking"
            ' after "manual delivery" wizard call with same date',
        )
        self.assertEqual(
            sum(first_picking.mapped("move_lines.product_uom_qty")), 7,
        )

    def test_04_sale_single_picking(self):
        """
        Test SO's various manual delivery
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product2.name,
                            "product_id": self.product2.id,
                            "product_uom_qty": 2.0,
                            "product_uom": self.product2.uom_id.id,
                            "price_unit": self.product2.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
            }
        )
        # confirm our standard so, check the picking
        order.action_confirm()
        # create a manual delivery for part of ordered quantity
        wizard = self._manual_delivery_wizard(order.order_line)
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids), 1.0, "Delivery: picking number should be 1.0"
        )

    def test_05_sale_multi_carrier(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 10.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.env.ref("product.list0").id,
                "manual_delivery": True,
                "carrier_id": self.carrier1.id,
            }
        )
        # confirm our standard so, check the picking
        order.action_confirm()
        # create a manual delivery for part of ordered quantity
        wizard = self._manual_delivery_wizard(order, {"carrier_id": self.carrier1.id})
        wizard.line_ids.write({"quantity": 2.0})
        wizard.confirm()
        # check picking is created
        self.assertEqual(
            len(order.picking_ids),
            1,
            'Picking should be created after "manual delivery" wizard call',
        )
        first_picking = order.picking_ids
        self.assertEqual(
            first_picking.carrier_id,
            order.carrier_id,
            "Picking carrier should be the one in the order",
        )
        # create a second manual delivery with a different carrier
        wizard = self._manual_delivery_wizard(order, {"carrier_id": self.carrier2.id})
        wizard.line_ids.write({"quantity": 2.0})
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids),
            2,
            "A different picking should've been created, as the carrier is different",
        )
        second_picking = order.picking_ids - first_picking
        self.assertEqual(
            second_picking.carrier_id,
            self.carrier2,
            "Picking carrier should be the one selected",
        )
        # create a third manual delivery for (should be mixed with first)
        wizard = self._manual_delivery_wizard(order, {"carrier_id": self.carrier1.id})
        wizard.line_ids.write({"quantity": 2.0})
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids), 2, "The first picking should be re-used",
        )
