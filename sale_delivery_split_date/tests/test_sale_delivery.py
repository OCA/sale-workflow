# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import format_date
from odoo.tests.common import TransactionCase
import datetime


class TestSaleDelivery(TransactionCase):

    def setUp(self):
        super(TestSaleDelivery, self).setUp()
        customer = self.env.ref('base.res_partner_3')
        p1 = self.env.ref('product.product_product_16')
        p2 = self.env.ref('product.product_product_25')
        today = datetime.datetime(2020, 1, 1)
        self.dt1 = today + datetime.timedelta(days=9)
        self.dt2 = today + datetime.timedelta(days=10)
        self.date_sooner = self.dt1
        self.date_later = self.dt2
        self.so = self._create_sale_order(customer)
        self.so_line1 = self._create_sale_order_line(
            self.so, p1, 10, 100.0, self.dt1)
        self.so_line2 = self._create_sale_order_line(
            self.so, p2, 10, 200.0, self.dt1)

    def _create_sale_order(self, customer):
        return self.env['sale.order'].create({'partner_id': customer.id})

    def _create_sale_order_line(self, sale, product, qty, price, date):
        return self.env['sale.order.line'].create({
            'product_id': product.id,
            'name': 'cool product',
            'order_id': sale.id,
            'price_unit': price,
            'product_uom_qty': qty,
            'commitment_date': date})

    def test_check_single_date(self):
        self.assertEqual(
            len(self.so.picking_ids), 0,
            "There must not be pickings for the SO when draft")
        self.so.action_confirm()
        self.assertEqual(
            len(self.so.picking_ids), 1,
            "There must be 1 picking for the SO when confirmed")
        self.assertEqual(
            self.so.picking_ids[0].scheduled_date.date(),
            self.so.picking_ids[0].min_dt)
        self.assertEqual(
            self.so.picking_ids[0].scheduled_date, self.date_sooner,
            "The picking must be planned at the expected date")
        self.assertEqual(
            self.so_line1.procurement_group_id,
            self.so_line2.procurement_group_id,
            "The procurement group must be the same")
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.procurement_group_id.name)

    def test_check_multiple_dates(self):
        # Change the date of the second line
        self.so_line2.commitment_date = self.dt2
        self.assertEqual(
            len(self.so.picking_ids), 0,
            "There must not be pickings for the SO when draft")
        self.so.action_confirm()
        self.assertEqual(
            len(self.so.picking_ids), 2,
            "There must be 2 pickings for the SO when confirmed")
        sorted_pickings = self.so.picking_ids.sorted(lambda x: x.scheduled_date)
        self.assertEqual(
            self.so.picking_ids[0].scheduled_date.date(),
            self.so.picking_ids[0].min_dt)
        self.assertEqual(
            sorted_pickings[0].scheduled_date, self.date_sooner,
            "The first picking must be planned at the soonest date")
        self.assertEqual(
            self.so.picking_ids[1].scheduled_date.date(),
            self.so.picking_ids[1].min_dt)
        self.assertEqual(
            sorted_pickings[1].scheduled_date, self.date_later,
            "The second picking must be planned at the latest date")
        self.assertNotEqual(
            self.so_line1.procurement_group_id,
            self.so_line2.procurement_group_id,
            "The procurement group must be different")
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.procurement_group_id.name)
        self.assertIn(
            format_date(self.env, self.date_later.date()),
            self.so_line2.procurement_group_id.name)

    def test_check_same_dates(self):
        # Change the date of the second line by just adding 1 hour
        same_date = self.dt1 + datetime.timedelta(hours=1)
        self.so_line2.commitment_date = same_date
        self.assertEqual(
            len(self.so.picking_ids), 0,
            "There must not be pickings for the SO when draft")
        self.so.action_confirm()
        self.assertEqual(
            len(self.so.picking_ids), 1,
            "There must be only one picking for the SO when confirmed")
        self.assertEqual(
            self.so.picking_ids[0].scheduled_date.date(),
            self.so.picking_ids[0].min_dt)
        self.assertEqual(
            self.so.picking_ids.scheduled_date, self.date_sooner,
            "The picking must be planned at the expected date")
        self.assertEqual(
            self.so_line1.procurement_group_id,
            self.so_line2.procurement_group_id,
            "The procurement group must be the same")
        self.assertIn(
            format_date(self.env, self.date_sooner.date()),
            self.so_line1.procurement_group_id.name)
