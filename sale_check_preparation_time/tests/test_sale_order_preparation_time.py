# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from datetime import datetime


class TestSaleOrderPreparationTime(TransactionCase):

    def setUp(self):
        super(TestSaleOrderPreparationTime, self).setUp()
        self.sale1 = self.env.ref('sale.sale_order_1')
        self.sale3 = self.env.ref('sale.sale_order_3')
        self.sale5 = self.env.ref('sale.sale_order_5')
        self.company = self.env.ref('base.main_company')
        self.company.order_limit_hour = 11.0
        self.company.tz = 'Europe/Brussels'

    def test_sale_confirmed_before_time_limit(self):
        self.sale1.action_confirm()
        self.sale1.confirmation_date = self.sale1.confirmation_date.replace(
            hour=10)
        self.picking1 = self.sale1.picking_ids[0]
        self.picking1.action_done()
        self.assertEquals(self.sale1.timely_delivery, True)

    def test_sale_confirmed_after_time_limit(self):
        self.sale3.action_confirm()
        self.sale3.confirmation_date = self.sale3.confirmation_date.replace(
            hour=15)
        self.picking3 = self.sale3.picking_ids[0]
        self.picking3.action_done()
        self.assertNotEquals(self.sale3.timely_delivery, True)

    def test_late_delivery(self):
        self.sale5.action_confirm()
        self.sale5.confirmation_date = self.sale5.confirmation_date.replace(
            day=(datetime.now().day - 3))
        self.picking5 = self.sale5.picking_ids[0]
        self.picking5.action_done()
        self.assertNotEquals(self.sale5.timely_delivery, True)
