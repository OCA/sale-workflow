# Copyright (C) 2018 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import datetime


class TestSaleStartEndDates(TransactionCase):

    def setUp(self):
        super(TestSaleStartEndDates, self).setUp()
        self.partner = self.env.ref('base.res_partner_3')
        self.product_id = self.env.ref('product.product_product_7')
        self.product_id.must_have_dates = True
        self.default_start_date = datetime.datetime.now()
        self.default_end_date = self.default_start_date + \
            datetime.timedelta(days=9)
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'default_start_date': self.default_start_date,
            'default_end_date': self.default_end_date,
            'pricelist_id': self.env.ref('product.list0').id,
            'order_line': [(0, 0, {
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'product_uom_qty': 2,
                'product_uom': self.product_id.uom_id.id,
                'price_unit': self.product_id.list_price,
            })],
        })
        self.so.action_confirm()
        for so_lines in self.so.order_line:
            so_lines.write({'start_date': self.default_start_date,
                            'end_date': self.default_end_date,
                            'number_of_days': 10})

    def test_default_start_date_change(self):
        with self.assertRaises(ValidationError):
            self.so.write({'default_start_date': self.default_end_date,
                           'default_end_date': self.default_start_date})
        self.so.default_start_date_change()

    def test_default_end_date_change(self):
        with self.assertRaises(ValidationError):
            self.so.write({'default_start_date': self.default_end_date,
                           'default_end_date': self.default_start_date})
        self.so.default_end_date_change()

    def test_start_end_dates_product_id_change(self):
        if self.so.default_end_date and self.so.default_end_date:
            self.so.order_line.start_end_dates_product_id_change()
            self.so.order_line.start_date_change()
            self.so.order_line.end_date_change()
            self.so.order_line.number_of_days_change()

    def test_start_end_dates_product_id(self):
        self.product_id.must_have_dates = False
        self.so.default_start_date = self.so.default_end_date = False
        self.so.order_line.start_end_dates_product_id_change()

    def test_number_of_days_change(self):
        self.product_id.must_have_dates = False
        self.so.order_line.start_date = False
        self.so.order_line.number_of_days_change()

    def test_end_date_change(self):
        self.product_id.must_have_dates = False
        self.so.order_line.write({'start_date': self.default_end_date,
                                  'end_date': self.default_start_date})
        self.so.order_line.end_date_change()

    def test_start_date_change(self):
        self.product_id.must_have_dates = False
        self.so.order_line.write({'start_date': self.default_end_date,
                                  'end_date': self.default_start_date})
        self.so.order_line.start_date_change()

    def test_constrains_end_dates(self):
        with self.assertRaises(ValidationError):
            self.so.order_line.end_date = False

    def test_constrains_start_date(self):
        with self.assertRaises(ValidationError):
            self.so.order_line.start_date = False

    def test_constrains_number_of_days(self):
        with self.assertRaises(ValidationError):
            self.so.order_line.number_of_days = 0.0

    def test_constrains_neg_number_of_days(self):
        with self.assertRaises(ValidationError):
            self.so.order_line.number_of_days = -1.0

    def test_constrains_not_equal_days(self):
        with self.assertRaises(ValidationError):
            self.so.order_line.number_of_days = 12

    def test_constrains_greater_st_date(self):
        with self.assertRaises(ValidationError):
            self.so.order_line.write({'start_date': self.default_end_date,
                                      'end_date': self.default_start_date})
