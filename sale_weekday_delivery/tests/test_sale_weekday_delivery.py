# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestSaleWeekdayDelivery(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.customer = cls.env["res.partner"].create(
            {"name": "ACME", "delivery_schedule_preference": "direct"}
        )
        cls.customer_shipping = cls.env["res.partner"].create(
            {
                "name": "Delivery address",
                "parent_id": cls.customer.id,
                "delivery_schedule_preference": "fix_weekdays",
                "delivery_schedule_monday": False,
                "delivery_schedule_tuesday": False,
                "delivery_schedule_wednesday": False,
                "delivery_schedule_thursday": True,
                "delivery_schedule_friday": False,
                "delivery_schedule_saturday": True,
                "delivery_schedule_sunday": False,
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
        return order

    def test_delivery_schedule_constraint(self):
        with self.assertRaises(ValidationError):
            self.customer_shipping.write(
                {
                    "delivery_schedule_thursday": False,
                    "delivery_schedule_saturday": False,
                }
            )

    @freeze_time("2020-03-24")  # Tuesday
    def test_delivery_schedule_expected_date(self):
        order = self._create_order()
        # We're tuesday and next weekday for delivery is thursday
        self.assertEqual(order.expected_date, fields.Datetime.to_datetime("2020-03-26"))
        # Ensure product customer lead time is considered
        # We're tuesday so + 3 days is friday, and next weekday for delivery
        #  is saturday 2020-03-28
        self.product.sale_delay = 3
        order_2 = self._create_order()
        # Play onchange manually to ensure customer_lead is set on the line
        order_2.order_line._onchange_product_id_set_customer_lead()
        self.assertEqual(
            order_2.expected_date, fields.Datetime.to_datetime("2020-03-28")
        )
        # Change the customer lead time directly on the line must also be
        #  considered
        # We're tuesday so + 5 days is sunday, and next weekday for delivery
        #  is thursday 2020-04-02
        order_2.order_line.customer_lead = 5
        self.assertEqual(
            order_2.expected_date, fields.Datetime.to_datetime("2020-04-02")
        )

    def test_preferred_weekdays(self):
        self.assertEqual(
            self.customer_shipping.get_delivery_schedule_preferred_weekdays(),
            ["thursday", "saturday"],
        )

    @freeze_time("2020-03-24")  # Tuesday
    def test_onchange_warnings(self):
        # Test warning on sale.order
        order = self._create_order()
        # Set to friday
        order.commitment_date = "2020-03-27"
        onchange_res = order._onchange_commitment_date()
        self.assertTrue("warning" in onchange_res.keys())
        # Set to saturday (preferred)
        order.commitment_date = "2020-03-28"
        onchange_res = order._onchange_commitment_date()
        self.assertIsNone(onchange_res)
        # Test warning on stock.picking
        order.action_confirm()
        picking = order.picking_ids
        # Set to friday
        picking.scheduled_date = "2020-03-27"
        onchange_res = picking._onchange_scheduled_date()
        self.assertTrue("warning" in onchange_res.keys())
        # Set to saturday (preferred)
        picking.scheduled_date = "2020-03-28"
        onchange_res = picking._onchange_scheduled_date()
        self.assertIsNone(onchange_res)

    @freeze_time("2020-03-24")  # Tuesday
    def test_prepare_procurement_values(self):
        # Without setting a commitment date, picking is scheduled for next
        #  preferred weekday
        order = self._create_order()
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26")
        )
        # Using a commitment date on a preferred weekday is perfectly fine
        order_2 = self._create_order()
        order_2.commitment_date = "2020-03-28"
        order_2.action_confirm()
        picking_2 = order_2.picking_ids
        self.assertEqual(
            picking_2.scheduled_date, fields.Datetime.to_datetime("2020-03-28")
        )
        # Using a commitment date on an weekday not preferred is still allowed
        order_3 = self._create_order()
        order_3.commitment_date = "2020-03-30"
        order_3.action_confirm()
        picking_3 = order_3.picking_ids
        self.assertEqual(
            picking_3.scheduled_date, fields.Datetime.to_datetime("2020-03-30")
        )
