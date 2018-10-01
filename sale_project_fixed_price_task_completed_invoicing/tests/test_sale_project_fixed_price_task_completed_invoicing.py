# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo.exceptions import UserError  # , ValidationError


class TestSaleProjectFixedPrice(TestSale):

    def test_sale_project_fixed_price(self):
        # The product comes from 'sale_timesheet' the only modification to add
        # is for the track_service
        prod_task = self.env.ref('product.product_product_1')
        prd_vals = {
            'track_service': 'completed_task',
        }
        prod_task.write(prd_vals)
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {'name': prod_task.name,
                                   'product_id': prod_task.id,
                                   'product_uom_qty': 1,
                                   'product_uom': prod_task.uom_id.id,
                                   'price_unit': prod_task.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        so = self.env['sale.order'].create(so_vals)
        so.action_confirm()

        # check task creation
        project = self.env.ref('sale_timesheet.project_GAP')
        task = project.task_ids.filtered(
            lambda t: t.name == '%s:%s' % (so.name, prod_task.name))
        self.assertTrue(task, 'Sale Service: task is not created')
        self.assertEqual(task.partner_id, so.partner_id,
                         'Sale Service: customer should be the same on task '
                         'and on SO')
        self.assertTrue(task.fixed_price)

        # check Task validation. It should update the delivered quantity
        line = so.order_line
        self.assertFalse(line.product_uom_qty == line.qty_delivered,
                         'Sale Service: line should be invoiced completely')
        task.toggle_invoiceable()
        self.assertTrue(task.invoiceable, 'The task should be invoiceable')
        self.assertTrue(line.product_uom_qty == line.qty_delivered,
                        'Sale Service: line should be invoiced completely')

        # Impossible to change task invoicable after validation of soline
        so.action_invoice_create()
        self.assertEqual(so.invoice_status,
                         'invoiced', 'SO should be invoiced')
        with self.assertRaises(UserError):
            task.toggle_invoiceable()
