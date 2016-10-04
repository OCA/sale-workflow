# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestSaleOrderType(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderType, self).setUp()
        self.sale_type_model = self.env['sale.order.type']
        self.sale_order_model = self.env['sale.order']
        self.invoice_model = self.env['account.invoice']
        self.partner = self.env.ref('base.res_partner_1')
        self.sequence = self.env['ir.sequence'].create({
            'name': 'Test Sales Order',
            'code': 'sale.order',
            'prefix': 'TSO',
            'padding': 3,
        })
        self.journal = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1)
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.product = self.env.ref('product.product_product_4')
        self.immediate_payment = self.env.ref(
            'account.account_payment_term_immediate')
        self.sale_pricelist = self.env.ref('product.list0')
        self.free_carrier = self.env.ref('stock.incoterm_FCA')
        self.sale_type = self.sale_type_model.create({
            'name': 'Test Sale Order Type',
            'sequence_id': self.sequence.id,
            'journal_id': self.journal.id,
            'warehouse_id': self.warehouse.id,
            'picking_policy': 'one',
            'payment_term_id': self.immediate_payment.id,
            'pricelist_id': self.sale_pricelist.id,
            'incoterm_id': self.free_carrier.id,
        })
        self.partner.sale_type = self.sale_type

    def test_sale_order_confirm(self):
        sale_line_dict = {
            'product_id': self.product.id,
            'name': self.product.name,
            'product_uom_qty': 1.0,
            'price_unit': self.product.lst_price,
        }
        vals = {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, sale_line_dict)]
        }
        sale_order = self.sale_order_model.create(vals)
        sale_order.onchange_type_id()
        sale_order.onchange_partner_id()
        sale_order.action_confirm()

    def test_invoice_onchange_type(self):
        invoice = self.invoice_model.new({'sale_type_id': self.sale_type.id})
        invoice.onchange_sale_type_id()
