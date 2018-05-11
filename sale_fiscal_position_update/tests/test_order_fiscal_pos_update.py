# © 2014 ToDay Akretion (http://www.akretion.com)
# © 2018 Roel Adriaans <roel@road-support.nl>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Roel Adriaans <roel@road-support.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
import time


class TestProductIdChange(AccountingTestCase):
    """Test that when an included tax is mapped by a fiscal position,
    when position fiscal change taxes and account wil be update on
    invoice lines.
    """

    def setUp(self):
        super(TestProductIdChange, self).setUp()
        self.order_model = self.env['sale.order']
        self.fiscal_position_model = self.env['account.fiscal.position']
        self.fiscal_position_tax_model = \
            self.env['account.fiscal.position.tax']
        self.fiscal_position_account_model = \
            self.env['account.fiscal.position.account']
        self.tax_model = self.env['account.tax']
        self.account_model = self.env['account.account']
        self.pricelist_model = self.env['product.pricelist']
        self.res_partner_model = self.env['res.partner']
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.invoice_line_model = self.env['account.invoice.line']
        self.account_user_type = self.env.ref(
            'account.data_account_type_revenue')
        self.account_receivable = self.env['account.account'].search(
            [('user_type_id', '=',
                self.env.ref('account.data_account_type_receivable').id)],
            limit=1)
        self.account_revenue = self.env['account.account'].search(
            [('user_type_id', '=',
                self.account_user_type.id)],
            limit=1)

    def test_fiscal_position_id_change(self):
        partner = self.res_partner_model.create(dict(name="George"))
        account_export_id = self.account_model.sudo().create({
            'code': "710000",
            'name': "customer export account",
            'user_type_id': self.account_user_type.id,
            'reconcile': True,
        })
        tax_sale = self.tax_model.create({
            'name': 'Sale tax',
            'type_tax_use': 'sale',
            'amount': '20.00',
        })

        tax_export_sale = self.tax_model.create({
            'name': "Export tax",
            'type_tax_use': 'sale',
            'amount': '0.00'
        })

        product_tmpl = self.product_tmpl_model.create({
            'name': 'Car',
            'lst_price': '15000',
            'taxes_id': [(6, 0, [tax_sale.id])],
            'property_account_income_id': self.account_revenue.id,

        })
        product = self.product_model.create({
            'product_tmpl_id': product_tmpl.id,
            'standard_price': '12000',
        })
        fp = self.fiscal_position_model.create({
            'name': "fiscal position export", 'sequence': 1,
        })

        fp_tax_sale = self.fiscal_position_tax_model.create({
            'position_id': fp.id,
            'tax_src_id': tax_sale.id,
            'tax_dest_id': tax_export_sale.id,
        })

        fp_account = self.fiscal_position_account_model.create({
            'position_id': fp.id,
            'account_src_id': self.account_revenue.id,
            'account_dest_id': account_export_id.id,
        })

        out_invoice = self.order_model.create({
            'partner_id': partner.id,
            'reference_type': 'none',
            'name': 'invoice to client',
            'account_id': self.account_receivable.id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-04-01',
        })
        out_line = self.invoice_line_model.create({
            'product_id': product.id,
            'price_unit': 15000,
            'quantity': 1,
            'invoice_id': out_invoice.id,
            'name': 'Car',
            'account_id': self.account_revenue.id,

        })

        out_line._onchange_product_id()
        self.assertEqual(
            out_line.invoice_line_tax_ids[0],
            tax_sale,
            "The sale tax off invoice line must be the same of product")
        out_invoice.fiscal_position_id = fp
        out_invoice.fiscal_position_change()
        self.assertEqual(
            out_line.invoice_line_tax_ids[0],
            fp_tax_sale.tax_dest_id,
            'The sale tax of invoice line must be changed by'
            ' fiscal position')
        self.assertEqual(
            out_line.account_id,
            fp_account.account_dest_id,
            'The account revenu of invoice line must be changed by'
            ' fiscal position')
