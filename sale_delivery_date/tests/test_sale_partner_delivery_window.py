# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from freezegun import freeze_time

from odoo import fields
from odoo.tests import SavepointCase


class TestSaleDeliveryWindow(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.customer = cls.env["res.partner"].create(
            {"name": "ACME", "delivery_time_preference": "anytime"}
        )
        cls.customer_shipping = cls.env["res.partner"].create(
            {
                "name": "Delivery address",
                "parent_id": cls.customer.id,
                "delivery_time_preference": "time_windows",
                "delivery_time_window_ids": [
                    (
                        0,
                        0,
                        {
                            "time_window_start": 8.0,
                            "time_window_end": 18.00,
                            "time_window_weekday_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        cls.env.ref(
                                            "base_time_window.time_weekday_thursday"
                                        ).id,
                                        cls.env.ref(
                                            "base_time_window.time_weekday_saturday"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ],
            }
        )
        cls.product = cls.env.ref("product.product_product_9")

    def _create_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "partner_shipping_id": self.customer_shipping.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    )
                ],
            }
        )
        # Play onchange manually to ensure customer_lead is set on the line
        order.order_line._onchange_product_id_set_customer_lead()
        return order

    @freeze_time("2020-03-24")  # Tuesday
    def test_delivery_schedule_expected_date(self):
        order = self._create_order()
        # We're tuesday and next delivery window is thursday
        self.assertEqual(
            order.expected_date, fields.Datetime.to_datetime("2020-03-26 08:00:00")
        )
        # Ensure product customer lead time is considered
        # We're tuesday so + 3 days is friday, and next delivery window
        #  is saturday 2020-03-28
        self.product.sale_delay = 3
        order_2 = self._create_order()
        self.assertEqual(
            order_2.expected_date, fields.Datetime.to_datetime("2020-03-28 08:00:00")
        )
        # Change the customer lead time directly on the line must also be
        #  considered
        # We're tuesday so + 5 days is sunday, and next delivery window
        #  is thursday 2020-04-02
        order_2.order_line.customer_lead = 5
        self.assertEqual(
            order_2.expected_date, fields.Datetime.to_datetime("2020-04-02 08:00:00")
        )

    @freeze_time("2020-03-24")  # Tuesday
    def test_onchange_warnings(self):
        # Test warning on sale.order
        order = self._create_order()
        # Set to friday
        order.commitment_date = "2020-03-27 08:00:00"
        onchange_res = order._onchange_commitment_date()
        self.assertEqual(
            onchange_res["warning"],
            order._commitment_date_no_delivery_window_match_msg(),
        )
        # Set to saturday (preferred)
        order.commitment_date = "2020-03-28 08:00:00"
        onchange_res = order._onchange_commitment_date()
        self.assertIsNone(onchange_res)
        # Test warning on stock.picking
        order.action_confirm()
        picking = order.picking_ids
        # Set to friday
        picking.scheduled_date = "2020-03-27 08:00:00"
        onchange_res = picking._onchange_scheduled_date()
        self.assertEqual(
            onchange_res["warning"],
            picking._scheduled_date_no_delivery_window_match_msg(),
        )
        # Set to saturday (preferred)
        picking.scheduled_date = "2020-03-28 08:00:00"
        onchange_res = picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)

    @freeze_time("2020-03-24 01:00:00")  # Tuesday
    def test_prepare_procurement_values(self):
        # Without setting a commitment date, picking is scheduled for next
        #  preferred delivery window start time
        order = self._create_order()
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 08:00:00")
        )
        # As long as we're not in a window, picking is scheduled for next
        #  preferred delivery window start time
        with freeze_time("2020-03-24 09:00:00"):
            order_2 = self._create_order()
            order_2.action_confirm()
            picking_2 = order_2.picking_ids
            self.assertEqual(
                picking_2.scheduled_date,
                fields.Datetime.to_datetime("2020-03-26 08:00:00"),
            )
        self.customer_shipping.delivery_time_window_ids.write(
            {
                "time_window_weekday_ids": [
                    (6, 0, [self.env.ref("base_time_window.time_weekday_thursday").id])
                ]
            }
        )
        # If we're before a window, picking is postponed to this window
        with freeze_time("2020-03-26 06:00:00"):
            order_3 = self._create_order()
            order_3.action_confirm()
            picking_3 = order_3.picking_ids
            self.assertEqual(
                picking_3.scheduled_date,
                fields.Datetime.to_datetime("2020-03-26 08:00:00"),
            )
        # If we're already in a window, picking is not postponed
        with freeze_time("2020-03-26 12:00:00"):
            order_3 = self._create_order()
            order_3.action_confirm()
            picking_3 = order_3.picking_ids
            self.assertEqual(
                picking_3.scheduled_date,
                fields.Datetime.to_datetime("2020-03-26 12:00:00"),
            )
        # If we're after delivery window on the only preferred weekday, picking
        # is postponed to next week
        with freeze_time("2020-03-26 20:00:00"):
            order_3 = self._create_order()
            order_3.action_confirm()
            picking_3 = order_3.picking_ids
            self.assertEqual(
                picking_3.scheduled_date,
                fields.Datetime.to_datetime("2020-04-02 08:00:00"),
            )
        # If we introduce a security lead time at company level, it must be
        #  considered to compute delivery date and schedule picking accordingly
        self.env.user.company_id.security_lead = 4
        with freeze_time("2020-03-26 20:00:00"):
            order_3 = self._create_order()
            order_3.action_confirm()
            picking_3 = order_3.picking_ids
            self.assertEqual(
                picking_3.scheduled_date,
                fields.Datetime.to_datetime("2020-03-29 08:00:00"),
            )
            self.assertEqual(
                picking_3.date_deadline,
                fields.Datetime.to_datetime("2020-04-02 08:00:00"),
            )

    @freeze_time("2020-03-24 01:00:00")  # Tuesday
    def test_prepare_procurement_values_commitment(self):
        # Using a commitment date on a preferred weekday is perfectly fine
        order = self._create_order()
        order.commitment_date = "2020-03-28 10:00:00"
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-28 10:00:00")
        )
        # Using a commitment date on an weekday not preferred is still allowed
        order_2 = self._create_order()
        order_2.commitment_date = "2020-03-30 06:00:00"
        order_2.action_confirm()
        picking_2 = order_2.picking_ids
        self.assertEqual(
            picking_2.scheduled_date, fields.Datetime.to_datetime("2020-03-30 06:00:00")
        )
