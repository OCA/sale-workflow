# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from datetime import timedelta

from freezegun import freeze_time

from odoo.tests import SavepointCase


class TestDeliveryDateInThePast(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.customer_partner = cls.env["res.partner"].create(
            {
                "name": "Partner cutoff",
                "order_delivery_cutoff_preference": "partner_cutoff",
                "cutoff_time": 9.0,
            }
        )
        cls.customer_warehouse = cls.env["res.partner"].create(
            {
                "name": "Partner warehouse cutoff",
                "order_delivery_cutoff_preference": "warehouse_cutoff",
                "cutoff_time": 9.0,
            }
        )

        company = cls.env.ref("base.main_company")
        # the global lead time will always plan 1 day before
        company.write({"security_lead": 1.00})

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
        return order

    def test_delivery_date_as_commitment_date(self):
        """Commitment date should be used as expected_delivery_date if
        set and not in the past"""
        with freeze_time("2021-10-15"):
            order = self._create_order(partner=self.customer_partner)
            order.commitment_date = "2021-10-20 09:00:00"
            order.action_confirm()
            picking = order.picking_ids
            self.assertEqual(picking.expected_delivery_date, order.commitment_date)

    def test_delivery_date_as_expected_date(self):
        """Expected date should be used if commitment_date isn't set and
        expected date is set but is not in the past.
        """
        with freeze_time("2021-10-15"):
            order = self._create_order(partner=self.customer_partner)
            order.action_confirm()
            picking = order.picking_ids
            self.assertEqual(picking.expected_delivery_date, order.expected_date)

    def test_delivery_date_as_late_confirm_expected_date(self):
        """If so has been confirmed late and there's no commitment_date,
        then expected_date is still valid, since it's updated when the
        so is confirmed.
        """
        with freeze_time("2021-10-15"):
            order = self._create_order(partner=self.customer_partner)
        with freeze_time("2021-10-25"):
            # according to docs/graph
            # order confirmation date = 2021-10-25 00:00:00
            # odoo_date_deadline = order_date + sol.customer_lead = 2021-10-26 00:00:00
            # date_order = odoo_date_deadline - sol.customer_lead = 2021-10-25 00:00:00
            # earliest_work_start = 2021-10-25 09:00:00 (cutoff applied)
            # earliest_work_start = 2021-10-25 09:00:00 (next calendar attendance)
            # earliest_expedition_date = earliest_work_start + workload = 2021-10-25 17:00:00
            # earliest_delivery_date = earliest_expedition_date + security_lead = 2021-10-26
            # final_delivery_date = earliest_delivery_date + customer delivery preference
            #                     = 2021-10-26
            order.action_confirm()
            picking = order.picking_ids
            self.assertEqual(str(order.expected_date.date()), "2021-10-26")
            self.assertEqual(str(picking.date.date()), "2021-10-25")
            self.assertEqual(picking.expected_delivery_date, order.expected_date)

    def test_delivery_date_as_late_scheduled_date(self):
        """Scheduled date should be used if both commitment_date and
        expected date are in the past, and if the picking is not done.
        """
        # confirm_date = 2021-10-15 00:00:00
        # with cutoff = 2021-10-15 08:00:00
        # working day = 2021-10-15 08:00:00
        # expedition_date = 2021-10-15 17:00:00
        # earliest delivery date = 2021-10-16 17:00:00
        # best_delivery_date : 2021-10-16 00:00:00 (no window)
        # ====
        # latest_expedition_date : 2021-10-16 17:00:00
        # best_expedition_date : 2021-10-16 17:00:00
        # latest_prepartion_date : 2021-10-15 08:00:00
        with freeze_time("2021-10-15"):
            order = self._create_order(partner=self.customer_partner)
            order.action_confirm()
        picking = order.picking_ids
        # Delivery date is kept as is, if no window is defined on the customer.
        self.assertEqual(str(picking.date_deadline), "2021-10-16 00:00:00")
        with freeze_time("2021-10-25"):
            # picking is handled late, order.commitment_date and
            # order.expected_date are outdated.
            # expected_delivery_date is postponed from now (as the expedition date)
            # with respect to customer's time window.
            td_security_lead = timedelta(days=picking.company_id.security_lead)
            self.assertEqual(str(picking.expected_delivery_date), "2021-10-26 00:00:00")

    def test_delivery_date_as_date_done(self):
        """Date done should be used if both commitment_date and
        expected date are in the past, and if the picking is done.
        """
        with freeze_time("2021-10-15"):
            order = self._create_order(partner=self.customer_partner)
            order.action_confirm()
            picking = order.picking_ids
        # Once picking has been set to done, the expected_delivery_date
        # is the picking's date done + security_lead and should never change
        td_security_lead = timedelta(days=picking.company_id.security_lead)
        with freeze_time("2021-10-20"):
            picking._action_done()
            expected_datetime = picking.date_done + td_security_lead
            self.assertEqual(picking.expected_delivery_date, expected_datetime)
        with freeze_time("2021-10-30"):
            self.assertEqual(picking.expected_delivery_date, expected_datetime)
