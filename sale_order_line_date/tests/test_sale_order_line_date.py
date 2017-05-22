# -*- coding: utf-8 -*-
# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp import fields
import datetime


class TestSaleOrderLineDates(TransactionCase):
    """Check the _get_shipped method of Sale Order. """

    def setUp(self):
        """Setup a Sale Order with 4 lines.
        And prepare procurements
        """
        super(TestSaleOrderLineDates, self).setUp()
        customer = self.env.ref('base.res_partner_3')
        self.product_ctg_model = self.env['product.category']
        self.company = self.env.ref('base.main_company')
        price = 100.0
        qty = 1000
        p1 = self._create_product(price)
        self._update_qty(p1, qty)
        today = datetime.datetime.now()
        dt1 = today + datetime.timedelta(days=9)
        dt2 = today + datetime.timedelta(days=10)
        self.dt3 = today + datetime.timedelta(days=3)
        self.sale1 = self._create_sale_order(customer, dt2)
        self.sale_line1 = self._create_sale_order_line(
            self.sale1, p1, qty, price, dt1
        )
        self.sale_line2 = self._create_sale_order_line(
            self.sale1, p1, qty, price, dt2
        )

    def _create_product(self, price):
        category = self.env.ref('product.product_category_1')
        product = self.env['product.product'].create({
            'name': 'test_product',
            'type': 'product',
            'standard_price': price,
            'list_price': price,
            'categ_id': category.id,
        })
        return product

    def _create_sale_order(self, customer, date):
        sale = self.env['sale.order'].create({
            'partner_id': customer.id,
            'partner_invoice_id': customer.id,
            'partner_shipping_id': customer.id,
            'requested_date': date
        })
        return sale

    def _create_sale_order_line(self, sale, product, qty, price, date):
        sale_line = self.env['sale.order.line'].create({
            'product_id': product.id,
            'name': 'cool product',
            'order_id': sale.id,
            'price_unit': price,
            'product_uom_qty': qty,
            'requested_date': date})
        return sale_line

    def _update_qty(self, product, qty):
        location_stock = self.env.ref('stock.stock_location_stock')
        wiz_obj = self.env['stock.change.product.qty']
        wiz = wiz_obj.create({'product_id': product.id,
                              'new_quantity': qty,
                              'location_id':  location_stock.id,
                              })
        wiz.change_product_qty()

    def test_procurement_scheduled_date(self):
        """True when matches the requested date in the sale_order_line"""
        self.sale1.action_confirm()
        procurements = self.env['procurement.order'].search([
            ('origin', '=', self.sale1.name),
            ('date_planned', '=', self.sale_line1.requested_date)])
        self.assertEqual(len(procurements), 1)
        procurements = self.env['procurement.order'].search([
            ('origin', '=', self.sale1.name),
            ('date_planned', '=', self.sale_line2.requested_date)])
        self.assertEqual(len(procurements), 1)

    def test_on_change_requested_date(self):
        """True when the requested date in the sale_order_line
        matches the requested date in the sale order"""
        req_date = fields.Datetime.to_string(self.dt3)
        self.sale1.write({'requested_date': self.dt3})
        result = self.sale1.onchange_requested_date(self.sale1.requested_date,
                                                    self.sale1.commitment_date)
        for line in result['value']['order_line']:
            self.assertEqual(line[2]['requested_date'], req_date)
