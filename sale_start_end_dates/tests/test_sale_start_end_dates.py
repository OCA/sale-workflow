# Copyright (C) 2018 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleStartEndDates(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_3")
        self.product_id = self.env.ref(
            "account_invoice_start_end_dates.product_insurance_contract_demo"
        )
        self.assertTrue(self.product_id.must_have_dates)
        self.product_no_dates = self.env.ref("product.product_product_7")
        self.assertFalse(self.product_no_dates.must_have_dates)
        self.default_start_date = datetime.datetime.now()
        self.default_end_date = self.default_start_date + datetime.timedelta(days=9)
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "default_start_date": self.default_start_date,
                "default_end_date": self.default_end_date,
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )
        self.order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.so.id,
                "name": self.product_id.display_name,
                "product_id": self.product_id.id,
                "product_uom_qty": 2,
                "product_uom": self.product_id.uom_id.id,
                "price_unit": self.product_id.list_price,
                "start_date": self.default_start_date,
                "end_date": self.default_end_date,
            }
        )
        self.so.action_confirm()

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
