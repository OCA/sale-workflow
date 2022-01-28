# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 ForgeFlow S.L. (https://forgeflow.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrderLineDates(TransactionCase):
    def setUp(self):
        """Setup a Sale Order with 4 lines."""
        super(TestSaleOrderLineDates, self).setUp()
        customer = self.env.ref("base.res_partner_3")
        price = 100.0
        qty = 5
        product_id = self.env.ref("product.product_product_7")
        self.today = fields.Datetime.now()
        self.dt1 = self.today + datetime.timedelta(days=9)
        self.dt2 = self.today + datetime.timedelta(days=10)
        self.dt3 = self.today + datetime.timedelta(days=3)
        self.sale1 = self._create_sale_order(customer, None)
        self.sale_line1 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, None
        )
        self.sale_line2 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, None
        )
        self.sale_line3 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, None
        )

    def _create_sale_order(self, customer, date):
        sale = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "partner_invoice_id": customer.id,
                "partner_shipping_id": customer.id,
                "commitment_date": date,
                "picking_policy": "direct",
            }
        )
        return sale

    def _create_sale_order_line(self, sale, product, qty, price, date):
        sale_line = self.env["sale.order.line"].create(
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

    def test_01_so_quotation_commitment_date(self):
        """Test if commitment date is correct in SO quotation"""
        self.assertEqual(self.sale1.commitment_date, False)
        self.sale_line1.write({"commitment_date": self.dt3})
        self.sale1._onchange_expected_date()
        self.assertEqual(self.sale1.commitment_date, self.dt3)
        self.sale_line2.write({"commitment_date": self.dt2})
        self.sale1._onchange_expected_date()
        self.assertEqual(self.sale1.commitment_date, self.dt3)
        self.sale1.picking_policy = "one"
        self.assertEqual(self.sale1.commitment_date, self.dt3)

    def test_02_so_commitment_date(self):
        """Test if commitment date is correct in SO quotation"""
        self.sale1.action_confirm()
        self.assertEqual(self.sale1.commitment_date, False)
        self.sale_line1.write({"commitment_date": self.dt3})
        self.sale1._onchange_expected_date()
        self.assertEqual(self.sale1.commitment_date, self.dt3)
        self.sale_line2.write({"commitment_date": self.dt2})
        self.sale1._onchange_expected_date()
        self.assertEqual(self.sale1.commitment_date, self.dt3)
        self.sale1.picking_policy = "one"
        self.assertEqual(self.sale1.commitment_date, self.dt3)

    def test_03_on_change_so_commitment_date(self):
        """Test if changing Delivery Date has repercussion in SO lines"""
        self.sale_line1.write({"commitment_date": self.dt1})
        self.sale_line2.write({"commitment_date": self.dt2})
        self.sale_line3.write({"commitment_date": self.dt3})
        self.sale1.action_confirm()
        self.sale1.write({"commitment_date": self.dt3})
        self.assertEqual(self.sale_line1.commitment_date, self.dt1)
        self.assertEqual(self.sale_line2.commitment_date, self.dt2)
        self.assertEqual(self.sale_line3.commitment_date, self.dt3)
