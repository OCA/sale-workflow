# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from freezegun import freeze_time

from odoo import fields
from odoo.tests import SavepointCase


class TestSaleCutoffDeliveryWindow(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.customer_partner = cls.env["res.partner"].create(
            {
                "name": "Partner cutoff",
                "order_delivery_cutoff_preference": "partner_cutoff",
                "cutoff_time": 9.0,
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
                                            "base_time_window.time_weekday_monday"
                                        ).id,
                                        cls.env.ref(
                                            "base_time_window.time_weekday_friday"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ],
            }
        )
        cls.customer_warehouse = cls.env["res.partner"].create(
            {
                "name": "Partner warehouse cutoff",
                "order_delivery_cutoff_preference": "warehouse_cutoff",
                "cutoff_time": 9.0,
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
                                            "base_time_window.time_weekday_monday"
                                        ).id,
                                        cls.env.ref(
                                            "base_time_window.time_weekday_friday"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ],
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"apply_cutoff": True, "cutoff_time": 10.0})
        cls.product = cls.env.ref("product.product_product_9")

    def _create_order(self, partner=None):
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_shipping_id": partner.id,
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

    @freeze_time("2020-03-26 18:00:00")  # thursday evening
    def test_after_cutoff_preferred_weekday(self):
        # After partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 09:00:00")
        )
        # Before warehouse cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 10:00:00")
        )

    @freeze_time("2020-03-27 08:00:00")  # friday morning
    def test_before_cutoff_preferred_weekday(self):
        # Before partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 09:00:00")
        )
        # Before warehouse cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 10:00:00")
        )

    @freeze_time("2020-03-27 18:00:00")  # friday evening
    def test_after_cutoff_other_weekday(self):
        # After partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        # After warehouse cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 10:00:00")
        )

    @freeze_time("2020-03-28 08:00:00")  # saturday morning
    def test_before_cutoff_other_weekday(self):
        # Before partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        # Before warehouse cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 10:00:00")
        )

    @freeze_time("2020-03-23 08:00:00")  # monday morning
    def test_before_cutoff_lead_time_preferred_weekday(self):
        self.product.sale_delay = 4
        # Before partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-23 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-27 09:00:00")
        )
        # Before partner cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-23 10:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-27 10:00:00")
        )

    @freeze_time("2020-03-23 18:00:00")  # monday evening
    def test_after_cutoff_lead_time_preferred_weekday(self):
        # THIS IS PROBABLY THE MOST IMPORTANT TEST HERE:
        #  This test ensures that cutoff is applied before delivery window
        #  because both sale_cutoff_time_delivery and sale_weekday_delivery
        #  override _get_procurement_values.
        # Also, at the beginning both modules had the same dependency and it
        #  did seem to work because sale_cutoff_time_delivery is alphabetically
        #  before sale_partner_delivery_window /!\
        #  Anyway, here we want the computation to happen as follows:
        #  confirmation time: 2020-03-23 18:00:00
        #  application of lead time: 2020-03-27 18:00:00
        #  application of cutoff: 2020-03-28 09:00:00
        #  application of weekday: 2020-03-30 08:00:00
        # what matches both cutoff and delivery window preference

        # If somehow the MRO of _prepare_procurement_values is WRONG we'd have:
        #  confirmation time: 2020-03-23 18:00:00
        #  application of lead time: 2020-03-27 18:00:00
        #  application of weekday: 2020-03-27 18:00:00
        #  application of cutoff: 2020-03-28 09:00:00
        # what doesn't match the delivery window preference!
        self.product.sale_delay = 4
        # Before partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 09:00:00")
        )
        # Before partner cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 10:00:00")
        )

    @freeze_time("2020-03-24 08:00:00")  # tuesday morning
    def test_before_cutoff_lead_time_other_weekday(self):
        self.product.sale_delay = 4
        # Before partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 09:00:00")
        )
        # Before partner cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 10:00:00")
        )

    @freeze_time("2020-03-24 18:00:00")  # tuesday evening
    def test_after_cutoff_lead_time_other_weekday(self):
        self.product.sale_delay = 4
        # Before partner cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )
        # Before partner cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 10:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )

    @freeze_time("2020-03-24 18:00:00")  # tuesday evening
    def test_partner_time_window_outside_cutoff_no_partner_cutoff(self):
        """Partner with a delivery time window not within cutoff

        And the partner has no cutoff. The cutoff of the warehouse must be applied.
        The expected time should not default to the delivery time window but to the
        warehouse cutoff.
        """
        partner = self.env["res.partner"].create(
            {
                "name": "Partner cutoff",
                "order_delivery_cutoff_preference": "partner_cutoff",
                "cutoff_time": 9.0,
                "delivery_time_preference": "time_windows",
                "delivery_time_window_ids": [
                    (
                        0,
                        0,
                        {
                            "time_window_start": 14.0,
                            "time_window_end": 15.00,
                            "time_window_weekday_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        self.env.ref(
                                            "base_time_window.time_weekday_monday"
                                        ).id,
                                        self.env.ref(
                                            "base_time_window.time_weekday_friday"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ],
            }
        )

        self.product.sale_delay = 4
        # Before partner cutoff
        order = self._create_order(partner=partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-26 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 14:00:00")
        )

    @freeze_time("2020-03-24 18:00:00")  # tuesday evening
    def test_partner_time_window_outside_cutoff_commitment_date(self):
        """Partner with a delivery time window not within cutoff

        And we set a commitment date on the sales order.
        """
        partner = self.env["res.partner"].create(
            {
                "name": "Partner cutoff",
                "order_delivery_cutoff_preference": "partner_cutoff",
                "cutoff_time": 9.0,
                "delivery_time_preference": "time_windows",
                "delivery_time_window_ids": [
                    (
                        0,
                        0,
                        {
                            "time_window_start": 14.0,
                            "time_window_end": 15.00,
                            "time_window_weekday_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        self.env.ref(
                                            "base_time_window.time_weekday_monday"
                                        ).id,
                                        self.env.ref(
                                            "base_time_window.time_weekday_friday"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ],
            }
        )

        self.product.sale_delay = 4
        # Before partner cutoff
        order = self._create_order(partner=partner)
        order.commitment_date = fields.Datetime.to_datetime("2020-04-03 15:00:00")
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-04-03 15:00:00")
        )
