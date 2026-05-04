# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import users

from odoo.addons.delivery.tests.common import DeliveryCommon
from odoo.addons.sale.tests.common import SaleCommon
from odoo.addons.stock.tests.common import TestStockCommon


class TestSaleStock(SaleCommon, DeliveryCommon, TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_vals = {
            "type": "consu",
            "list_price": 20.0,
            "categ_id": cls.product_category.id,
            "is_storable": True,
        }
        cls.product, cls.product2, cls.product3 = cls.env["product.product"].create(
            [
                {
                    **product_vals,
                    "name": "Test Product",
                    "invoice_policy": "delivery",
                },
                {
                    **product_vals,
                    "name": "Test Product 2",
                    "invoice_policy": "delivery",
                },
                {
                    **product_vals,
                    "name": "Test Product 3",
                    "invoice_policy": "order",
                },
            ]
        )
        cls.carrier1 = cls.carrier
        cls.carrier2 = cls._prepare_carrier(
            product=cls._prepare_carrier_product(
                name="Normal Delivery Charges",
                list_price=10.0,
            ),
            name="Normal Delivery Charges",
            delivery_type="fixed",
            fixed_price=10.0,
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.stock_location, 100
        )
        cls.sale_user.group_ids += cls.env.ref("stock.group_stock_user")

    def _manual_delivery_wizard(self, records, vals=None):
        if not vals:
            vals = {}
        return (
            self.env["manual.delivery"]
            .with_context(
                active_model=records._name,
                active_ids=records.ids,
            )
            .create(vals)
        )

    def _get_order_line_vals(self, qty=5, product=False):
        if not product:
            product = self.product
        return Command.create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom_id": product.uom_id.id,
                "price_unit": product.list_price,
            }
        )

    def _create_order(
        self, qty=5, product=False, manual_delivery=True, order_line_vals=False
    ):
        if not order_line_vals:
            order_line_vals = [self._get_order_line_vals(qty, product)]
        return (
            self.env["sale.order"]
            .with_user(self.sale_user)
            .create(
                {
                    "partner_id": self.partner.id,
                    "partner_invoice_id": self.partner.id,
                    "partner_shipping_id": self.partner.id,
                    "order_line": order_line_vals,
                    "manual_delivery": manual_delivery,
                }
            )
        )

    @users("salesman")
    def test_00_sale_manual_delivery(self):
        """
        Test SO's manual delivery; we do it with a user without admin rights
        """
        order = self._create_order()
        # confirm our standard so, check the picking
        order.action_confirm()
        self.assertFalse(
            order.picking_ids,
            'No picking should be created for "manual delivery" orders',
        )
        # Raise error when user try to modify sale order in confirmd stage.
        with self.assertRaises(UserError):
            order.write({"manual_delivery": False})
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

    def test_01_sale_standard_delivery(self):
        """
        Test SO's standard delivery
        """
        order = self._create_order(manual_delivery=False)
        # confirm our standard so, check the picking
        order.action_confirm()
        self.assertTrue(
            order.picking_ids,
            'Picking should be created for "standard delivery" orders',
        )
        # deliver completely
        pick = order.picking_ids
        pick.action_assign()
        pick.move_line_ids.write({"quantity": 5})
        pick.button_validate()
        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in order.order_line)
        self.assertEqual(del_qty, 5.0, "Delivery quantity doesn't match")

    def test_02_sale_various_manual_delivery(self):
        """
        Test SO's various manual delivery
        """
        order = self._create_order()
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
        # checking has_pending_delivery for Create Delivery button to appear
        self.assertTrue(order.has_pending_delivery)
        # check picking is created
        self.assertEqual(
            len(order.picking_ids),
            1,
            'Picking should be created after "manual delivery" wizard call',
        )
        # deliver completely
        pick = order.picking_ids
        pick.action_assign()
        pick.move_line_ids.write({"quantity": 2})
        pick.button_validate()
        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in order.order_line)
        self.assertEqual(del_qty, 2.0, "Delivery quantity doesn't match")
        # a manual delivery with qty 0 shouldn't do anything
        wizard = self._manual_delivery_wizard(order)
        wizard.line_ids.write({"quantity": 0.0})
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids),
            1.0,
            "No picking should've been created",
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
        # checking has_pending_delivery for Create Delivery button to hide
        self.assertFalse(order.has_pending_delivery)
        self.assertEqual(
            len(order.picking_ids),
            2.0,
            "Picking number doesn't match",
        )

    def test_03_sale_selected_lines(self):
        """
        Test SO's various manual delivery
        """
        order1 = self._create_order(qty=1)
        order2 = self._create_order(qty=2, product=self.product2)
        order3 = self._create_order(qty=3, product=self.product3)
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
            len(order3.picking_ids.move_ids),
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
            undelivered,
            order2.order_line,
            "Bad pending qty to deliver filter",
        )

    def test_03_sale_multi_delivery(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product2, self.stock_location, 100
        )
        line_vals = [
            self._get_order_line_vals(qty=10),
            self._get_order_line_vals(qty=10, product=self.product2),
        ]
        order = self._create_order(order_line_vals=line_vals)

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
            sum(first_picking.mapped("move_ids.product_uom_qty")),
            7,
        )

    def test_04_sale_single_picking(self):
        """
        Test SO's various manual delivery
        """
        line_vals = [
            self._get_order_line_vals(qty=1),
            self._get_order_line_vals(qty=2, product=self.product2),
        ]
        order = self._create_order(order_line_vals=line_vals)
        # confirm our standard so, check the picking
        order.action_confirm()
        # create a manual delivery for part of ordered quantity
        wizard = self._manual_delivery_wizard(order.order_line)
        wizard.confirm()
        self.assertEqual(
            len(order.picking_ids), 1.0, "Delivery: picking number should be 1.0"
        )

    def test_05_sale_multi_carrier(self):
        order = self._create_order(qty=10)
        order.carrier_id = self.carrier1
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
            len(order.picking_ids),
            2,
            "The first picking should be re-used",
        )
