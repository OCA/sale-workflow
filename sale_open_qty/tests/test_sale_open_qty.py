# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestSaleOpenQty(TransactionCase):
    def setUp(self):
        super(TestSaleOpenQty, self).setUp()
        self.sale_order_model = self.env['sale.order']
        sale_order_line_model = self.env['sale.order.line']
        partner_model = self.env['res.partner']
        prod_model = self.env['product.product']
        analytic_account_model = self.env['account.analytic.account']
        self.product_uom_model = self.env['product.uom']

        pa_dict = {
            'name': 'Partner 1',
            'supplier': True,
        }
        self.partner = partner_model.sudo().create(pa_dict)
        so_dict = {
            'partner_id': self.partner.id,
        }
        # Sale Order Num 1
        self.sale_order_1 = self.sale_order_model.create(so_dict)
        uom_id = self.product_uom_model.search([
            ('name', '=', 'Unit(s)')])[0].id
        pr_dict = {
            'name': 'Product Test',
            'uom_id': uom_id,
        }
        self.product = prod_model.sudo().create(pr_dict)
        ac_dict = {
            'name': 'analytic account 1',
        }
        self.analytic_account_1 = \
            analytic_account_model.sudo().create(ac_dict)
        sl_dict1 = {
            'customer_lead': 0.0,
            'name': 'PO01',
            'order_id': self.sale_order_1.id,
            'product_id': self.product.id,
            'product_uom': uom_id,
            'price_unit': 1.0,
            'product_uom_qty': 5.0,
        }
        self.sale_order_line_1 = \
            sale_order_line_model.sudo().create(sl_dict1)
        self.sale_order_1.action_confirm()

    def test_compute_qty_to_deliver(self):
        self.assertEqual(self.sale_order_line_1.qty_to_deliver, 5.0,
                         "Expected 5 as qty_to_deliver in the SO line")
        self.assertEqual(self.sale_order_1.qty_to_invoice, 5.0,
                         "Expected 5 as qty_to_invoice in the SO")
        self.assertEqual(self.sale_order_1.qty_to_deliver, 5.0,
                         "Expected 5 as qty_to_deliver in the SO")

    def test_search_qty_to_invoice_and_deliver(self):
        found = self.sale_order_model.search(
            ['|', ('qty_to_invoice', '>', 0.0), ('qty_to_deliver', '>', 0.0)])
        self.assertTrue(
            self.sale_order_1.id in found.ids,
            'Expected SO %s in SOs %s' % (self.sale_order_1.id, found.ids))
