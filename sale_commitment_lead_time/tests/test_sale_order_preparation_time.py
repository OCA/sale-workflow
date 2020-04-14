# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from datetime import datetime


class TestSaleOrderPreparationTime(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderPreparationTime, cls).setUpClass()
        cls.sale1 = cls.env.ref('sale.sale_order_1')
        cls.sale3 = cls.env.ref('sale.sale_order_3')
        cls.sale5 = cls.env.ref('sale.sale_order_5')
        cls.company = cls.env.ref('base.main_company')
        cls.company.check_preparation_time = False
        cls.company.order_limit_hour = 0.0
        cls.company.tz = ''
        cls.config_settings = cls.env['res.config.settings'].create({
            'group_sale_order_dates': True,
            'check_preparation_time': True,
            'order_limit_hour': 11.0,
            'tz': 'Europe/Brussels'})
        cls.config_settings.get_values()
        cls.config_settings.set_values()

    def test_settings_on_company(self):
        self.assertEquals(self.company.check_preparation_time, True)
        self.assertEquals(self.company.order_limit_hour, 11.0)
        self.assertEquals(self.company.tz, 'Europe/Brussels')

    def test_sale_confirmed_before_time_limit(self):
        self.sale1.action_confirm()
        self.sale1.confirmation_date = self.sale1.confirmation_date.replace(
            hour=10)
        self.sale1.picking_ids.move_line_ids.write({'qty_done': 1})
        self.sale1.picking_ids.action_done()
        self.assertEquals(self.sale1.on_time_delivery, True)

    def test_sale_confirmed_after_time_limit(self):
        self.sale3.action_confirm()
        self.sale3.confirmation_date = self.sale3.confirmation_date.replace(
            hour=15)
        self.sale3.picking_ids.move_line_ids.write({'qty_done': 1})
        self.sale3.picking_ids.action_done()
        self.assertNotEquals(self.sale3.on_time_delivery, True)

    def test_late_delivery(self):
        self.sale5.action_confirm()
        self.sale5.confirmation_date = self.sale5.confirmation_date.replace(
            day=(datetime.now().day - 3))
        self.sale5.picking_ids.move_line_ids.write({'qty_done': 1})
        self.sale5.picking_ids.action_done()
        self.assertNotEquals(self.sale5.on_time_delivery, True)
