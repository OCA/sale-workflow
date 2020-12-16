# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from freezegun import freeze_time

from odoo import fields
from odoo.tests import SavepointCase


class TestSaleCutoffTimeDelivery(SavepointCase):
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

    @freeze_time("2020-03-25 08:00:00")
    def test_before_cutoff_time_delivery(self):
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-24 09:00:00")
        )
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-24 10:00:00")
        )

    @freeze_time("2020-03-25 18:00:00")
    def test_after_cutoff_time_delivery(self):
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-25 09:00:00")
        )
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-25 10:00:00")
        )

    @freeze_time("2020-03-25 07:00:00")
    def test_before_cutoff_time_delivery_tz(self):
        self.customer_partner.tz = "Europe/Brussels"
        self.warehouse.tz = "Europe/Brussels"
        # Frozen time is 2020-03-25 07:00:00 UTC, or 2020-03-25 08:00:00 GMT+1
        # what is before cutoff times
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-24 08:00:00")
        )
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-24 09:00:00")
        )

    @freeze_time("2020-03-25 18:00:00")
    def test_after_cutoff_time_delivery_tz(self):
        self.customer_partner.tz = "Europe/Brussels"
        self.warehouse.tz = "Europe/Brussels"
        # Frozen time is 2020-03-25 18:00:00 UTC, or 2020-03-25 19:00:00 GMT+1
        # what is after cutoff times
        order = self._create_order(partner=self.customer_partner)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-25 08:00:00")
        )
        order = self._create_order(partner=self.customer_warehouse)
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-25 09:00:00")
        )

    @freeze_time("2020-03-25 08:00:00")
    def test_commitment_date(self):
        """Order with a commitment date

        The transfer's scheduled date is set by odoo according to the
        lead time, but the time must be the cut-off's time.
        """
        order = self._create_order(partner=self.customer_partner)
        order.commitment_date = fields.Datetime.to_datetime("2020-03-28 15:00:00")
        order.action_confirm()

        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 09:00:00")
        )

        order = self._create_order(partner=self.customer_warehouse)
        order.commitment_date = fields.Datetime.to_datetime("2020-03-28 15:00:00")
        order.action_confirm()
        picking = order.picking_ids
        self.assertEqual(
            picking.scheduled_date, fields.Datetime.to_datetime("2020-03-27 10:00:00")
        )
