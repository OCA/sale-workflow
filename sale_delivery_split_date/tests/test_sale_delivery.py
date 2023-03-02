# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.tests.common import TransactionCase
from odoo.tools import format_date


class TestSaleDelivery(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        customer = cls.env.ref("base.res_partner_3")
        p1 = cls.env.ref("product.product_product_16")
        p2 = cls.env.ref("product.product_product_25")
        today = datetime.datetime(2020, 1, 1)
        cls.dt1 = today + datetime.timedelta(days=9)
        cls.dt2 = today + datetime.timedelta(days=10)
        cls.date_sooner = cls.dt1
        cls.date_later = cls.dt2
        cls.so = cls._create_sale_order(customer)
        cls.so_line1 = cls._create_sale_order_line(cls.so, p1, 10, 100.0, cls.dt1)
        cls.so_line2 = cls._create_sale_order_line(cls.so, p2, 10, 200.0, cls.dt1)

    @classmethod
    def _create_sale_order(cls, customer):
        return cls.env["sale.order"].create({"partner_id": customer.id})

    @classmethod
    def _create_sale_order_line(cls, sale, product, qty, price, date):
        return cls.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "name": "cool product",
                "order_id": sale.id,
                "price_unit": price,
                "product_uom_qty": qty,
                "commitment_date": date,
            }
        )

    def test_check_single_date(self):
        self.assertEqual(
            len(self.so.picking_ids),
            0,
            "There must not be pickings for the SO when draft",
        )
        self.so.action_confirm()
        self.assertEqual(
            len(self.so.picking_ids),
            1,
            "There must be 1 picking for the SO when confirmed",
        )
        self.assertEqual(
            self.so.picking_ids[0].scheduled_date,
            self.date_sooner,
            "The picking must be planned at the expected date",
        )
        self.assertEqual(
            self.so_line1.procurement_group_id,
            self.so_line2.procurement_group_id,
            "The procurement group must be the same",
        )
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.procurement_group_id.name,
        )

    def test_check_multiple_dates(self):
        # Change the date of the second line
        self.so_line2.commitment_date = self.dt2
        self.assertEqual(
            len(self.so.picking_ids),
            0,
            "There must not be pickings for the SO when draft",
        )
        self.so.action_confirm()
        self.assertEqual(
            len(self.so.picking_ids),
            2,
            "There must be 2 pickings for the SO when confirmed",
        )
        sorted_pickings = self.so.picking_ids.sorted(lambda x: x.scheduled_date)
        self.assertEqual(
            sorted_pickings[0].scheduled_date,
            self.date_sooner,
            "The first picking must be planned at the soonest date",
        )
        self.assertEqual(
            sorted_pickings[1].scheduled_date,
            self.date_later,
            "The second picking must be planned at the latest date",
        )
        self.assertNotEqual(
            self.so_line1.procurement_group_id,
            self.so_line2.procurement_group_id,
            "The procurement group must be different",
        )
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.procurement_group_id.name,
        )
        self.assertIn(
            format_date(self.env, self.date_later.date()),
            self.so_line2.procurement_group_id.name,
        )

    def test_check_same_dates(self):
        # Change the date of the second line by just adding 1 hour
        same_date = self.dt1 + datetime.timedelta(hours=1)
        self.so_line2.commitment_date = same_date
        self.assertEqual(
            len(self.so.picking_ids),
            0,
            "There must not be pickings for the SO when draft",
        )
        self.so.action_confirm()
        self.assertEqual(
            len(self.so.picking_ids),
            1,
            "There must be only one picking for the SO when confirmed",
        )
        self.assertEqual(
            self.so.picking_ids.scheduled_date,
            self.date_sooner,
            "The picking must be planned at the expected date",
        )
        self.assertEqual(
            self.so_line1.procurement_group_id,
            self.so_line2.procurement_group_id,
            "The procurement group must be the same",
        )
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.procurement_group_id.name,
        )
