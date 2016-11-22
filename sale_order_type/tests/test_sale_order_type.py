# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


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
        self.product_sale = self.env['account.account'].create({
            'code': 'X2020',
            'name': 'Product Sales - (test)',
            'user_type_id': self.env.ref(
                'account.data_account_type_revenue').id,
            'tag_ids': [(6, 0,
                         [self.env.ref('account.account_tag_operating').id])],
        })
        self.journal = self.env['account.journal'].create({
            'name': 'Customer Invoices - Test',
            'code': 'TINV',
            'type': 'sale',
            'default_debit_account_id': self.product_sale.id,
            'default_credit_account_id': self.product_sale.id,
            'refund_sequence': True,
        })
        self.refund_journal = self.env['account.journal'].create({
            'name': 'Sales Credit Note Journal - (test)',
            'code': 'TSCNJ',
            'type': 'general',
            'default_debit_account_id': self.product_sale.id,
            'default_credit_account_id': self.product_sale.id,
            'refund_sequence': True,
        })
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.product = self.env.ref('product.product_product_4')
        self.sale_type_id = self.sale_type_model.create({
            'name': 'Test Sale Order Type',
            'sequence_id': self.sequence.id,
            'journal_id': self.journal.id,
            'refund_journal_id': self.refund_journal.id,
            'warehouse_id': self.warehouse.id,
            'picking_policy': 'one',
        })
        self.partner.sale_type_id = self.sale_type_id
        self.sale_order = self.sale_order_model.create({
            'partner_id': self.env.ref('base.res_partner_2').id,
        })

    def test_sale_order_onchange_partner(self):
        self.sale_order.partner_id = self.partner
        self.sale_order.onchange_partner_id()
        self.assertEqual(self.sale_order.type_id.id,
                         self.partner.sale_type_id.id)

    def test_sale_order_onchange_type(self):
        sale_order = self.sale_order_model.new(
            {'type_id': self.sale_type_id.id})
        sale_order.onchange_type_id()
        self.assertEqual(self.sale_type_id.warehouse_id,
                         sale_order.warehouse_id)
        self.assertEqual(self.sale_type_id.picking_policy,
                         sale_order.picking_policy)
