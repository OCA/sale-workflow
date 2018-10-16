# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestSaleOrderTypeRule(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderTypeRule, self).setUp()
        self.invoice_model = self.env['account.invoice']
        self.sale_order_model = self.env['sale.order']
        self.sale_type_model = self.env['sale.order.type']
        self.sale_type_rule_model = self.env['sale.order.type.rule']
        self.product_model = self.env['product.product']

        self.account = self.env.ref('l10n_generic_coa.1_conf_a_recv')
        self.partner = self.env.ref('base.res_partner_1')
        self.product1, self.product2 = self.product_model.search([], limit=2)
        self.product_category = self.product2.categ_id

        self.sale_type_prod = self.create_sale_type('Product')
        self.sale_type_prod.write({'rule_ids': [(0, 0, {
            'name': 'Product',
            'product_ids': [(4, self.product1.id)]})]})

        self.sale_type_categ = self.create_sale_type('Category')
        self.sale_type_categ.write({'rule_ids': [(0, 0, {
            'name': 'Category',
            'product_category_ids': [(4, self.product_category.id)]})]})

    def create_sale_type(self, name):
        self.sequence = self.env['ir.sequence'].create({
            'name': 'Test Sales Order',
            'code': 'sale.order',
            'prefix': 'TSO',
            'padding': 3,
        })
        self.journal = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1)
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.immediate_payment = self.env.ref(
            'account.account_payment_term_immediate')
        self.sale_pricelist = self.env.ref('product.list0')
        self.free_carrier = self.env.ref('stock.incoterm_FCA')
        return self.sale_type_model.create({
            'name': name,
            'sequence_id': self.sequence.id,
            'journal_id': self.journal.id,
            'warehouse_id': self.warehouse.id,
            'picking_policy': 'one',
            'payment_term_id': self.immediate_payment.id,
            'pricelist_id': self.sale_pricelist.id,
            'incoterm_id': self.free_carrier.id
        })

    def prepare_sale_order_vals(self, product_ids):
        sale_line_vals_list = list(dict())
        for product_id in product_ids:
            sale_line_vals_list.append({
                'product_id': product_id.id,
                'name': product_id.name,
                'product_uom_qty': 1.0,
                'price_unit': product_id.lst_price,
            })
        return {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, sale_line_vals)
                           for sale_line_vals in sale_line_vals_list]
        }

    def prepare_invoice_vals(self, product_ids):
        invoice_line_vals_list = list(dict())
        for product_id in product_ids:
            invoice_line_vals_list.append({
                'account_id': self.account.id,
                'product_id': product_id.id,
                'name': product_id.name,
                'product_uom_qty': 1.0,
                'price_unit': product_id.lst_price,
            })
        return {
            'account_id': self.account.id,
            'partner_id': self.partner.id,
            'invoice_line_ids': [
                (0, 0, invoice_line_vals)
                for invoice_line_vals in invoice_line_vals_list]
        }

    def test_sale_match_product(self):
        sale_order_vals = self.prepare_sale_order_vals(self.product1)
        sale_order = self.sale_order_model.create(sale_order_vals)

        sale_order.match_order_type()

        self.assertEqual(sale_order.type_id, self.sale_type_prod)

    def test_sale_match_category(self):
        sale_order_vals = self.prepare_sale_order_vals(self.product2)
        sale_order = self.sale_order_model.create(sale_order_vals)

        sale_order.match_order_type()

        self.assertEqual(sale_order.type_id, self.sale_type_categ)

    def test_sale_match_product_category(self):
        """ If a sale order has both product and category matching,
        choose the rule having the product."""
        sale_order_vals = self.prepare_sale_order_vals(
            self.product1 + self.product2)
        sale_order = self.sale_order_model.create(sale_order_vals)

        sale_order.match_order_type()

        self.assertEqual(sale_order.type_id, self.sale_type_prod)

    def test_invoice_match_product(self):
        invoice_vals = self.prepare_invoice_vals(self.product1)
        invoice = self.invoice_model.create(invoice_vals)

        invoice.match_order_type()

        self.assertEqual(invoice.sale_type_id, self.sale_type_prod)

    def test_invoice_match_category(self):
        invoice_vals = self.prepare_invoice_vals(self.product2)
        invoice = self.invoice_model.create(invoice_vals)

        invoice.match_order_type()

        self.assertEqual(invoice.sale_type_id, self.sale_type_categ)

    def test_invoice_match_product_category(self):
        """ If a sale order has both product and category matching,
        choose the rule having the product."""
        invoice_vals = self.prepare_invoice_vals(
            self.product1 + self.product2)
        invoice = self.invoice_model.create(invoice_vals)

        invoice.match_order_type()

        self.assertEqual(invoice.sale_type_id, self.sale_type_prod)
