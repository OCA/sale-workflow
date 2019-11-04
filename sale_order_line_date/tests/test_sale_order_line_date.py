# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields
import datetime


class TestSaleOrderLineDates(TransactionCase):

    def setUp(self):
        """Setup a Sale Order with 4 lines.
        """
        super(TestSaleOrderLineDates, self).setUp()
        customer = self.env.ref('base.res_partner_3')
        price = 100.0
        qty = 5
        product_id = self.env.ref('product.product_product_7')
        today = fields.Datetime.now()
        dt1 = today + datetime.timedelta(days=9)
        dt2 = today + datetime.timedelta(days=10)
        self.dt3 = today + datetime.timedelta(days=3)
        self.sale1 = self._create_sale_order(customer, dt2)
        self.sale_line1 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, dt1)
        self.sale_line2 = self._create_sale_order_line(
            self.sale1, product_id, qty, price, dt2)
        self.sale_line2.write({'commitment_date': dt2})
        self.sale1.action_confirm()

    def _create_sale_order(self, customer, date):
        sale = self.env['sale.order'].create({
            'partner_id': customer.id,
            'partner_invoice_id': customer.id,
            'partner_shipping_id': customer.id,
            'commitment_date': date
        })
        return sale

    def _create_sale_order_line(self, sale, product, qty, price, date):
        sale_line = self.env['sale.order.line'].create({
            'product_id': product.id,
            'name': 'cool product',
            'order_id': sale.id,
            'price_unit': price,
            'product_uom_qty': qty,
            'commitment_date': date})
        return sale_line

    def test_on_change_commitment_date(self):
        """True when the commitment date in the sale_order_line
        matches the commitment date in the sale order"""
        self.sale1.write({'commitment_date': self.dt3})
        result = self.sale1._onchange_commitment_date()
        for line in result['value']['order_line']:
            self.assertEqual(line[2]['commitment_date'], self.dt3)
