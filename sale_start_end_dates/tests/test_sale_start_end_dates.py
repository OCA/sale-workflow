# Copyright (C) 2018 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleStartEndDates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product_id = cls.env["product.product"].create(
            {
                "name": "Test insurance",
                "type": "service",
                "must_have_dates": True,
                "list_price": 1200,
            }
        )
        cls.product_no_dates = cls.env["product.product"].create(
            {
                "name": "My test product",
                "type": "service",
                "must_have_dates": False,
                "list_price": 2400,
            }
        )
        cls.default_start_date = datetime.datetime.now()
        cls.default_end_date = cls.default_start_date + datetime.timedelta(days=9)
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "default_start_date": cls.default_start_date,
                "default_end_date": cls.default_end_date,
            }
        )
        cls.order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.so.id,
                "product_id": cls.product_id.id,
                "product_uom_qty": 2,
                "price_unit": cls.product_id.list_price,
                "start_date": cls.default_start_date,
                "end_date": cls.default_end_date,
            }
        )
        cls.so.action_confirm()

    def test_default_start_end_date_constraint(self):
        with self.assertRaises(ValidationError):
            self.so.write(
                {
                    "default_start_date": self.default_end_date,
                    "default_end_date": self.default_start_date,
                }
            )

    def test_compute_start_end_date(self):
        new_line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_id.id,
                "name": self.product_id.display_name,
                "product_uom_qty": 2,
                "product_uom": self.product_id.uom_id.id,
                "order_id": self.so.id,
            }
        )
        self.assertEqual(new_line.start_date, self.so.default_start_date)
        self.assertEqual(new_line.end_date, self.so.default_end_date)

    def test_compute_product_no_dates(self):
        new_line = self.env["sale.order.line"].create(
            {
                "product_id": self.product_no_dates.id,
                "name": self.product_no_dates.display_name,
                "product_uom_qty": 2,
                "product_uom": self.product_no_dates.uom_id.id,
                "order_id": self.so.id,
            }
        )
        self.assertFalse(new_line.start_date)
        self.assertFalse(new_line.end_date)

    def test_compute_number_of_days(self):
        self.assertEqual(self.order_line.number_of_days, 10)

    def test_inverse_number_of_days(self):
        self.order_line.number_of_days = 1
        self.assertEqual(self.order_line.start_date, self.order_line.end_date)
        self.order_line.number_of_days = -1
        self.assertEqual(self.order_line.number_of_days, 1)

    def test_prepare_invoice_line(self):
        invoice_line_vals = self.order_line._prepare_invoice_line()
        self.assertEqual(invoice_line_vals["product_id"], self.product_id.id)
        self.assertEqual(invoice_line_vals["start_date"], self.order_line.start_date)
        self.assertEqual(invoice_line_vals["end_date"], self.order_line.end_date)
