# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestSaleOrderType(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderType, self).setUp()
        self.sale_type_model = self.env['sale.order.type']
        self.sale_order_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']
        self.picking_model = self.env['stock.picking']
        self.partner = self.env.ref('base.res_partner_1')
        self.sequence = self.env['ir.sequence'].create({
            'name': 'Test Sales Order',
            'code': 'sale.order',
            'prefix': 'TSO',
            'padding': 3,
        })
        self.journal = self.env.ref('account.sales_journal')
        self.refund_journal = self.env.ref('account.refund_sales_journal')
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.product = self.env.ref('product.product_product_4')
        self.sale_type = self.sale_type_model.create({
            'name': 'Test Sale Order Type',
            'sequence_id': self.sequence.id,
            'journal_id': self.journal.id,
            'refund_journal_id': self.refund_journal.id,
            'warehouse_id': self.warehouse.id,
            'picking_policy': 'one',
            'order_policy': 'picking',
            'invoice_state': '2binvoiced',
        })
        self.partner.sale_type = self.sale_type

    def test_sale_order_onchange_partner(self):
        onchange_partner = self.sale_order_model.onchange_partner_id(
            self.partner.id)
        self.assertEqual(self.sale_type.id,
                         onchange_partner['value']['type_id'])

    def test_sale_order_onchange_type(self):
        sale_order = self.sale_order_model.new({'type_id': self.sale_type.id})
        sale_order.onchange_type_id()
        self.assertEqual(self.sale_type.warehouse_id,
                         sale_order.warehouse_id)
        self.assertEqual(self.sale_type.picking_policy,
                         sale_order.picking_policy)
        self.assertEqual(self.sale_type.order_policy, sale_order.order_policy)

    def test_sale_order_confirm(self):
        sale_order_dict = self.sale_order_model.onchange_partner_id(
            self.partner.id)['value']
        sale_order_dict['partner_id'] = self.partner.id
        sale_line_dict = {
            'product_id': self.product.id,
            'name': self.product.name,
            'product_uom_qty': 1.0,
            'price_unit': self.product.lst_price,
        }
        sale_order_dict['order_line'] = [(0, 0, sale_line_dict)]
        sale_order = self.sale_order_model.create(sale_order_dict)
        sale_order.onchange_type_id()
        sale_order.action_button_confirm()
        for picking in sale_order.picking_ids:
            self.assertEqual(self.sale_type.invoice_state,
                             picking.invoice_state)
