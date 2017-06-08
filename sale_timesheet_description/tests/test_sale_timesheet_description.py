# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.sale.tests.test_sale_common import TestSale


class TestSaleTimesheetDescription(TestSale):
    def test_sale_timesheet_description(self):
        """ Test invoice description """
        inv_obj = self.env['account.invoice']
        # intial so
        prod_ts = self.env.ref('product.product_product_2')
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': prod_ts.name,
                'product_id': prod_ts.id,
                'product_uom_qty': 5,
                'product_uom': prod_ts.uom_id.id,
                'price_unit': prod_ts.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        so = self.env['sale.order'].create(so_vals)
        so.action_confirm()
        # let's log some timesheets
        self.env['account.analytic.line'].create({
            'name': 'Test description 1234567890',
            'account_id': so.project_id.id,
            'unit_amount': 10.5,
            'user_id': self.manager.id,
            'is_timesheet': True,
        })
        inv_id = so.action_invoice_create()
        inv = inv_obj.browse(inv_id)
        description = inv.invoice_line_ids[0].name
        self.assertIn('Test description 1234567890', description)
