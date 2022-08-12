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
        # Parameters:
        #   - customer_lead = 0
        #   - security_lead = 0
        #   - date_order = "2020-03-27 18:00" (Friday)
        #   - partner's delivery time window: Monday & Friday 08:00-18:00
        # Expected result:
        #   With partner's cutoff set to 09:00:
        #   - date_planned = "2020-03-30 09:00" (customer wants to be delivered
        #     on Monday starting at 8AM, but employees will start working on it
        #     at 9AM - partner's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        #   With warehouse's cutoff set to 10:00:
        #   - date_planned = "2020-03-30 10:00" (customer wants to be delivered
        #     on Monday starting at 8AM, but employees will start working on it
        #     at 10AM - WH's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        # With partner's cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )
        # With warehouse's cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 10:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )

    @freeze_time("2020-03-28 08:00:00")  # saturday morning
    def test_before_cutoff_other_weekday(self):
        # Parameters:
        #   - customer_lead = 0
        #   - security_lead = 0
        #   - date_order = "2020-03-28 08:00" (Saturday)
        #   - partner's delivery time window: Monday & Friday 08:00-18:00
        # Expected result:
        #   With partner's cutoff set to 09:00:
        #   - date_planned = "2020-03-30 09:00" (partner's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (same day but can't promise 08:00)
        #   With warehouse's cutoff set to 10:00:
        #   - date_planned = "2020-03-30 10:00" (customer_lead and WH's cutoff)
        #   - date_deadline = "2020-03-30 10:00" (same day but can't promise 08:00)
        self.product.sale_delay = 0
        self.env.company.security_lead = 0
        # With partner's cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )
        # With warehouse's cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 10:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )

    @freeze_time("2020-03-23 08:00:00")  # monday morning
    def test_before_cutoff_lead_time_preferred_weekday(self):
        # Parameters:
        #   - customer_lead = 4
        #   - security_lead = 0
        #   - date_order = "2020-03-23 08:00" (Monday)
        #   - partner's delivery time window: Monday & Friday 08:00-18:00
        # Expected result:
        #   With partner's cutoff set to 09:00:
        #   - date_planned = "2020-03-27 09:00" (customer_lead and partner's cutoff)
        #   - date_deadline = "2020-03-27 09:00" (same day but can't promise 08:00)
        #   With warehouse's cutoff set to 10:00:
        #   - date_planned = "2020-03-27 10:00" (customer_lead and WH's cutoff)
        #   - date_deadline = "2020-03-27 10:00" (same day but can't promise 08:00)
        self.product.sale_delay = 4
        self.env.company.security_lead = 0
        # With partner's cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-27 09:00:00")
        )
        # With warehouse's cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 10:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-27 10:00:00")
        )

    @freeze_time("2020-03-23 18:00:00")  # monday evening
    def test_after_cutoff_lead_time_preferred_weekday(self):
        # Parameters:
        #   - customer_lead = 4
        #   - security_lead = 0
        #   - date_order = "2020-03-23 18:00" (Monday)
        #   - partner's delivery time window: Monday & Friday 08:00-18:00
        # Expected result:
        #   With partner's cutoff set to 09:00:
        #   - date_planned = "2020-03-30 09:00" (customer_lead and partner's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        #   With warehouse's cutoff set to 10:00:
        #   - date_planned = "2020-03-30 10:00" (customer_lead and WH's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        self.product.sale_delay = 4
        self.env.company.security_lead = 0
        # With partner's cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )
        # With warehouse's cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 10:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )

    @freeze_time("2020-03-24 08:00:00")  # tuesday morning
    def test_before_cutoff_lead_time_other_weekday(self):
        # Parameters:
        #   - customer_lead = 4
        #   - security_lead = 0
        #   - date_order = "2020-03-24 08:00" (Tuesday)
        #   - partner's delivery time window: Monday & Friday 08:00-18:00
        # Expected result:
        #   With partner's cutoff set to 09:00:
        #   - date_planned = "2020-03-30 09:00" (customer_lead and partner's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        #   With warehouse's cutoff set to 10:00:
        #   - date_planned = "2020-03-28 10:00" (customer_lead and partner's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        self.product.sale_delay = 4
        self.env.company.security_lead = 0
        # With partner's cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )
        # With warehouse's cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 10:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 08:00:00")
        )

    @freeze_time("2020-03-24 18:00:00")  # tuesday evening
    def test_after_cutoff_lead_time_other_weekday(self):
        # Parameters:
        #   - customer_lead = 4
        #   - security_lead = 0
        #   - date_order = "2020-03-24 18:00" (Tuesday)
        #   - partner's delivery time window: Monday & Friday 08:00-18:00
        # Expected result:
        #   With partner's cutoff set to 09:00:
        #   - date_planned = "2020-03-30 09:00" (customer_lead and partner's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        #   With warehouse's cutoff set to 10:00:
        #   - date_planned = "2020-03-30 10:00" (customer_lead and partner's cutoff)
        #   - date_deadline = "2020-03-30 08:00" (next time window is Monday 08:00)
        self.product.sale_delay = 4
        self.env.company.security_lead = 0
        # With partner's cutoff
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            # With respect to partner's cutoff
            picking.scheduled_date,
            fields.Datetime.to_datetime("2020-03-30 09:00:00"),
        )
        self.assertEqual(
            # With respect to partner's delivery time window
            picking.date_deadline,
            fields.Datetime.to_datetime("2020-03-30 08:00:00"),
        )
        # With warehouse's cutoff
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            # With respect to warehouse's cutoff
            picking.scheduled_date,
            fields.Datetime.to_datetime("2020-03-30 10:00:00"),
        )
        self.assertEqual(
            # With respect to partner's delivery time window
            picking.date_deadline,
            fields.Datetime.to_datetime("2020-03-30 08:00:00"),
        )

    @freeze_time("2020-03-24 18:00:00")  # tuesday evening
    def test_partner_time_window_outside_cutoff_no_partner_cutoff(self):
        """Partner with a delivery time window not within cutoff

        And the partner has no cutoff. The cutoff of the warehouse must be applied.
        The expected time should not default to the delivery time window but to the
        warehouse cutoff.
        """
        # FIXME: the docstring says the partner has no cutoff but the code below
        # set it to 09:00, so currently this test is a duplicate
        # of 'test_after_cutoff_lead_time_other_weekday'
        # Parameters:
        #   - customer_lead = 4
        #   - security_lead = 0
        #   - date_order = "2020-03-24 18:00" (Tuesday)
        #   - partner's cutoff set to 09:00
        #   - partner's delivery time window: Monday & Friday 14:00-15:00
        # Expected result:
        #   - date_planned = "2020-03-30 09:00" (customer_lead and partner's cutoff)
        #   - date_deadline = "2020-03-30 14:00" (next time window is Monday 14:00)
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
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-30 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-03-30 14:00:00")
        )

    @freeze_time("2020-03-24 18:00:00")  # tuesday evening
    def test_partner_time_window_outside_cutoff_commitment_date(self):
        """Partner with a delivery time window not within cutoff

        And we set a commitment date on the sales order.
        """
        # Parameters:
        #   - customer_lead = 4 (ignored if a commitment_date is provided)
        #   - security_lead = 1
        #   - date_order = "2020-03-24 18:00" (Tuesday)
        #   - commitment_date = "2020-04-03 15:00" (Friday)
        #   - partner's delivery time window: Monday & Friday 14:00-15:00
        # Expected result:
        #   - date_planned = "2020-04-02 09:00" (security lead time + cutoff)
        #   - date_deadline = commitment_date
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
        self.env.company.security_lead = 1
        order = self._create_order(partner=partner)
        order.commitment_date = fields.Datetime.to_datetime("2020-04-03 15:00:00")
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-04-02 09:00:00")
        )
        self.assertEqual(
            picking.date_deadline, fields.Datetime.to_datetime("2020-04-03 15:00:00")
        )
