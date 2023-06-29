# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016-22 ForgeFlow S.L. (https://forgeflow.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrderLineDates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Setup a Sale Order with 4 lines."""
        super().setUpClass()
        customer = cls.env.ref("base.res_partner_3")
        cls.company = cls.env.ref("base.main_company")
        cls.company.security_lead = 1

        price = 100.0
        qty = 5
        product_id = cls.env.ref("product.product_product_7")
        cls.today = fields.Datetime.now()
        cls.dt1 = cls.today + datetime.timedelta(days=9)
        cls.dt2 = cls.today + datetime.timedelta(days=10)
        cls.dt3 = cls.today + datetime.timedelta(days=3)
        cls.sale1 = cls._create_sale_order(customer, cls.dt2)
        cls.sale_line1 = cls._create_sale_order_line(
            cls.sale1, product_id, qty, price, cls.dt1
        )
        cls.sale_line2 = cls._create_sale_order_line(
            cls.sale1, product_id, qty, price, cls.dt2
        )
        cls.sale_line3 = cls._create_sale_order_line(
            cls.sale1, product_id, qty, price, None
        )
        cls.sale2 = cls._create_sale_order(customer, cls.dt2)
        cls.sale_line4 = cls._create_sale_order_line(
            cls.sale2, product_id, qty, price, cls.dt3
        )
        cls.sale_line5 = cls._create_sale_order_line(
            cls.sale2, product_id, qty, price, cls.dt2
        )
        cls.sale_line6 = cls._create_sale_order_line(
            cls.sale2, product_id, qty, price, cls.dt1
        )

    @classmethod
    def _create_sale_order(cls, customer, date):
        sale = cls.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "partner_invoice_id": customer.id,
                "partner_shipping_id": customer.id,
                "commitment_date": date,
                "picking_policy": "direct",
            }
        )
        return sale

    @classmethod
    def _create_sale_order_line(cls, sale, product, qty, price, date):
        sale_line = cls.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "name": "cool product",
                "order_id": sale.id,
                "price_unit": price,
                "product_uom_qty": qty,
                "commitment_date": date,
            }
        )
        return sale_line

    def _assert_equal_dates(self, date1, date2):
        if isinstance(date1, datetime.datetime):
            date1 = date1.date()
        if isinstance(date2, datetime.datetime):
            date2 = date2.date()
        self.assertEqual(date1, date2)

    def test_01_so_commitment_dates(self):
        """Test if commitment date in sale_order_line fills
        with SO commitment_date only when is empty"""
        self.assertEqual(self.sale_line3.commitment_date, False)
        self.assertEqual(self.sale1.commitment_date, self.dt2)
        self.sale1.write({"commitment_date": self.dt3})
        self.sale1._onchange_commitment_date()
        self.assertEqual(self.sale_line1.commitment_date, self.dt1)
        self.assertEqual(self.sale_line2.commitment_date, self.dt2)
        self.assertEqual(self.sale_line3.commitment_date, self.dt3)

    def test_02_shipping_policies(self):
        """Test if dates are propagated correctly taking into
        account Shipping Policy"""
        self.sale1.action_confirm()
        picking = self.sale1.picking_ids
        self.assertEqual(len(picking), 1)
        # it should be the earliest (3 line commitment_date is not set) -> dt1
        self.assertEqual(picking.scheduled_date, self.dt1 - datetime.timedelta(days=1))
        self.assertEqual(picking.date_deadline, self.dt1)
        self.assertEqual(self.sale2.picking_policy, "direct")
        self.sale2.picking_policy = "one"
        self.sale2.action_confirm()
        picking = self.sale2.picking_ids
        self.assertEqual(len(picking), 1)
        # It should be the latest -> dt2
        self.assertEqual(picking.scheduled_date, self.dt2 - datetime.timedelta(days=1))
        self.assertEqual(picking.date_deadline, self.dt2)
        # security_lead 1 day.
        self._assert_equal_dates(
            self.sale_line4.commitment_date - datetime.timedelta(days=1),
            self.sale_line4.move_ids.date,
        )
        self._assert_equal_dates(
            self.sale_line4.commitment_date, self.sale_line4.move_ids.date_deadline
        )
        self._assert_equal_dates(
            self.sale_line5.commitment_date - datetime.timedelta(days=1),
            self.sale_line5.move_ids.date,
        )
        self._assert_equal_dates(
            self.sale_line5.commitment_date, self.sale_line5.move_ids.date_deadline
        )
        self._assert_equal_dates(
            self.sale_line6.commitment_date - datetime.timedelta(days=1),
            self.sale_line6.move_ids.date,
        )
        self._assert_equal_dates(
            self.sale_line6.commitment_date, self.sale_line6.move_ids.date_deadline
        )

    def test_03_line_commitment_date_picking_propagation(self):
        """Test if dates are propagated correctly in stock moves"""
        self.sale1.write({"commitment_date": self.dt1})
        self.sale1._onchange_commitment_date()
        self._assert_equal_dates(self.sale_line3.commitment_date, self.dt1)
        self.sale1.action_confirm()
        # security_lead 1 day.
        self._assert_equal_dates(
            self.sale_line1.commitment_date - datetime.timedelta(days=1),
            self.sale_line1.move_ids.date,
        )
        self._assert_equal_dates(
            self.sale_line1.commitment_date, self.sale_line1.move_ids.date_deadline
        )
        self._assert_equal_dates(
            self.sale_line2.commitment_date - datetime.timedelta(days=1),
            self.sale_line2.move_ids.date,
        )
        self._assert_equal_dates(
            self.sale_line2.commitment_date, self.sale_line2.move_ids.date_deadline
        )
        self._assert_equal_dates(
            self.sale_line3.commitment_date - datetime.timedelta(days=1),
            self.sale_line3.move_ids.date,
        )
        self._assert_equal_dates(
            self.sale_line3.commitment_date, self.sale_line3.move_ids.date_deadline
        )
        # Test line date change after confirmation
        self.sale_line1.write({"commitment_date": self.dt2})
        self._assert_equal_dates(
            self.sale_line1.commitment_date, self.sale_line1.move_ids.date_deadline
        )
