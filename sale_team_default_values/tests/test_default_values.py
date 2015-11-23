#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
from openerp.tests.common import TransactionCase


class TestDefaultValues(TransactionCase):

    def test_propagate_defaults(self):
        self.so.onchange_section_id()
        self.so.action_button_confirm()
        self.assertEqual(self.so.project_id, self.team.project_id)
        self.assertEqual(self.so.fiscal_position, self.position)
        self.assertEqual(self.so.pricelist_id, self.pricelist)
        self.so.action_invoice_create()
        invoice = self.so.invoice_ids
        self.assertEqual(1, len(invoice))
        self.assertEqual(invoice.journal_id, self.team.journal_id)

    def setUp(self):
        super(TestDefaultValues, self).setUp()

        self.team = self.env.ref('sales_team.section_sales_department')
        self.position = self.env['account.fiscal.position'].create({
            'name': 'more tax',
        })
        self.pricelist = self.env['product.pricelist'].create({
            'name': 'super expensive',
            'type': 'sale',
        })
        self.team.write({
            'payment_term':
            self.env.ref('account.account_payment_term_15days').id,
            'fiscal_position': self.position.id,
            'pricelist_id': self.pricelist.id,
            'warehouse_id': self.env.ref('stock.stock_warehouse_shop0').id,
            'project_id': self.env.ref('account.analytic_nebula').id,
            'journal_id': self.env.ref('account.miscellaneous_journal').id
        })

        customer = self.env.ref('base.res_partner_3')
        self.my_partner = self.env.user.company_id.partner_id

        product = self.env.ref('product.product_product_9')

        self.so = self.env['sale.order'].create({
            'partner_id': customer.id,
            'section_id': self.team.id,
        })
        self.sol = self.env['sale.order.line'].create({
            'name': '/',
            'order_id': self.so.id,
            'product_id': product.id,
        })
