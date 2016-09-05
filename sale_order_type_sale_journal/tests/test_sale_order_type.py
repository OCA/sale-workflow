# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.tests.common as common


class TestSaleOrderType(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderType, self).setUp()
        self.sale_type_model = self.env['sale.order.type']
        self.sale_order_model = self.env['sale.order']
        self.inv_type_model = self.env['sale_journal.invoice.type']
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.inv_type = self.inv_type_model.create({
            'name': 'test inv type'
        })
        self.sale_type = self.sale_type_model.create({
            'name': 'Test Sale Order Type',
            'invoice_type_id': self.inv_type.id,
            'warehouse_id': self.warehouse.id,
        })

    def test_sale_order_onchange_type(self):
        sale_order = self.sale_order_model.new({'type_id': self.sale_type.id})
        sale_order.onchange_type_id_sale_journal()
        self.assertEqual(self.sale_type.invoice_type_id,
                         sale_order.invoice_type_id)
