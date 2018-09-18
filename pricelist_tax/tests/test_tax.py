# coding: utf-8
# © 2018  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TaxCase(TransactionCase):

    def setUp(self):
        super(TaxCase, self).setUp()
        self.ht_plist = self.env.ref('pricelist_tax.ht_pricelist')
        self.ttc_plist = self.env.ref('pricelist_tax.ttc_pricelist')
        self.fp_intra = self.env.ref(
            'l10n_fr.1_fiscal_position_template_intraeub2b').id
        self.fp_exp = self.env.ref(
            'l10n_fr.1_fiscal_position_template_import_export').id
        self.solo = self.env['sale.order.line']

    def _create_sale_order(self, pricelist):
        # Creating a sale order
        return self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_10').id,
            'pricelist_id': pricelist.id,
        })

    def test_tax_ht(self):
        sale = self._create_sale_order(self.ht_plist)
        ak_product = self.env.ref('pricelist_tax.ak_product')
        vals = {
            'product_uom_qty': 1,
            'product_id': ak_product.id,
            'order_id': sale.id,
        }
        vals = self.env['sale.order.line'].play_onchanges(vals, vals.keys())
        sale.write({'order_line': [(0, 0, vals)]})
        expected_amount = 7.0
        self._common_checks('ht test:', sale, expected_amount)

    def test_tax_ttc(self):
        sale = self._create_sale_order(self.ttc_plist)
        ak_product = self.env.ref('pricelist_tax.ak_product')
        vals = {
            'product_uom_qty': 1,
            'product_id': ak_product.id,
            'order_id': sale.id,
        }
        vals = self.env['sale.order.line'].play_onchanges(vals, vals.keys())
        sale.write({'order_line': [(0, 0, vals)]})
        expected_amount = 6.67
        self._common_checks('ttc test:', sale, expected_amount)

    def _common_checks(self, test, sale, amount):
        used_tax = sale.order_line[0].tax_id
        self.assertEqual(
            sale.order_line[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
        sale.write({'fiscal_position_id': self.fp_intra})
        self.assertEqual(
            sale.order_line[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
        sale.write({'fiscal_position_id': False})
        self.assertEqual(sale.order_line[0].tax_id, used_tax,
                         "%s Tax on sale without fisc. pos. is not the same "
                         "after tried/reverted another fisc. pos. " % test)
        self.assertEqual(
            sale.order_line[0].price_subtotal, amount,
            "%s Bad price_subtotal" % test)
