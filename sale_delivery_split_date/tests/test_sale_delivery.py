# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.tools import format_date

from odoo.addons.sale_stock.tests.common import TestSaleStockCommon


class TestSaleDelivery(TestSaleStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        customer = cls.partner_a
        p1 = cls._create_product(
            name="test_product1",
            is_storable=True,
        )
        p2 = cls._create_product(
            name="test_product2",
            is_storable=True,
        )
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
            self.so_line1.stock_reference_id,
            self.so_line2.stock_reference_id,
            "The procurement group must be the same",
        )
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.stock_reference_id.name,
        )

    def test_wo_a_date(self):
        self.assertEqual(
            len(self.so.picking_ids),
            0,
            "There must not be pickings for the SO when draft",
        )
        self.so_line1.commitment_date = False
        self.so.action_confirm()

        self.assertIn(
            self.so.name,
            self.so_line1.stock_reference_id.name,
            "W/o Commitment Date stock reference equal to [SO Name]",
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
            self.so_line1.stock_reference_id,
            self.so_line2.stock_reference_id,
            "The procurement group must be different",
        )
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.stock_reference_id.name,
        )
        self.assertIn(
            format_date(self.env, self.date_later.date()),
            self.so_line2.stock_reference_id.name,
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
            self.so_line1.move_ids.date_deadline,
            self.so_line1.commitment_date,
            "First SO Line move deadline must be equal to commitment date",
        )
        self.assertEqual(
            self.so_line2.move_ids.date_deadline,
            self.so_line2.commitment_date,
            "Second SO Line move deadline must be equal to commitment date",
        )

        self.assertEqual(
            self.so_line1.stock_reference_id,
            self.so_line2.stock_reference_id,
            "The procurement group must be the same",
        )
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.stock_reference_id.name,
        )

    def test_security_lead_time_same_dates(self):
        same_date = self.dt1 + datetime.timedelta(hours=1)
        self.so_line2.commitment_date = same_date
        self.so.company_id.security_lead = 2
        security_date = self.date_sooner - datetime.timedelta(days=2)
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
            security_date,
            "The picking must be planned at the expected date "
            "(with security lead time)",
        )
        self.assertEqual(
            self.so_line1.move_ids.date_deadline,
            self.so_line1.commitment_date,
            "First SO Line move deadline must be equal to commitment date",
        )
        self.assertEqual(
            self.so_line2.move_ids.date_deadline,
            self.so_line2.commitment_date,
            "Second SO Line move deadline must be equal to commitment date",
        )
        self.assertEqual(
            self.so_line1.stock_reference_id,
            self.so_line2.stock_reference_id,
            "The procurement group must be the same",
        )
        self.assertIn(
            format_date(self.env, security_date.date()),
            self.so_line1.stock_reference_id.name,
        )

    def test_security_lead_time_multiple_dates(self):
        self.so_line2.commitment_date = self.dt2
        self.so.company_id.security_lead = 3
        security_date_sooner = self.date_sooner - datetime.timedelta(days=3)
        security_date_later = self.date_later - datetime.timedelta(days=3)
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
            security_date_sooner,
            "The first picking must be planned at the soonest date "
            "(with security lead time)",
        )
        self.assertEqual(
            sorted_pickings[0].date_deadline,
            self.so_line1.commitment_date,
            "The picking deadline must be equal to commitment date",
        )
        self.assertEqual(
            sorted_pickings[1].scheduled_date,
            security_date_later,
            "The second picking must be planned at the latest date "
            "(with security lead time)",
        )
        self.assertEqual(
            sorted_pickings[1].date_deadline,
            self.so_line2.commitment_date,
            "The picking deadline must be equal to commitment date",
        )
        self.assertNotEqual(
            self.so_line1.stock_reference_id,
            self.so_line2.stock_reference_id,
            "The procurement group must be different",
        )
        self.assertIn(
            format_date(self.env, security_date_sooner.date()),
            self.so_line1.stock_reference_id.name,
        )
        self.assertIn(
            format_date(self.env, security_date_later.date()),
            self.so_line2.stock_reference_id.name,
        )
