# coding: utf-8
# 2017 EBII Monsieurb <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleGenerator(TransactionCase):
    def setUp(self):
        super(TestSaleGenerator, self).setUp()
        self.partner1 = self.env.ref('base.res_partner_address_4')
        self.partner2 = self.env.ref('base.res_partner_address_27')
        self.sale = self.env.ref('sale.sale_order_4')

    def test_partner_create(self):
        sale_tmpl = self.sale
        sale_tmpl.is_template = True
        part1 = self.partner1
        part2 = self.partner2
        vals = {
            'name': '/',
            'partner_ids': [(4, part1.id, 0), (4, part2.id, 0)],
            'tmpl_sale_id': sale_tmpl.id,
            'warehouse_id': self.env.ref('stock.stock_warehouse_shop0').id,
            'state': 'draft',
            'company_id': self.ref('base.main_company'),
        }
        sg = self.env['sale.generator'].create(vals)

        sg.button_update_order()

        sales = self.env['sale.order'].search([('generator_id', '=', sg.id)])
        self.assertEqual(len(sales), 2)
        for sale in sales:
            self.assertEqual(sale.state, 'draft')

        sg.action_confirm()
        for sale in sales:
            self.assertEqual(sale.state, 'sale')
