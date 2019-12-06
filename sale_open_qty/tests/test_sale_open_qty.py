# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.fields import Datetime


class TestSaleOpenQty(TransactionCase):
    def setUp(self):
        super(TestSaleOpenQty, self).setUp()
        self.sale_order_model = self.env['sale.order']
        sale_order_line_model = self.env['sale.order.line']
        partner_model = self.env['res.partner']
        prod_model = self.env['product.product']
        analytic_account_model = self.env['account.analytic.account']
        self.product_uom_model = self.env['product.uom']

        # partners
        pa_dict = {
            'name': 'Partner 1',
            'supplier': True,
        }
        self.partner = partner_model.sudo().create(pa_dict)
        pa_dict2 = {
            'name': 'Partner 2',
            'supplier': True,
        }
        self.partner2 = partner_model.sudo().create(pa_dict2)

        # account
        ac_dict = {
            'name': 'analytic account 1',
        }
        self.analytic_account_1 = \
            analytic_account_model.sudo().create(ac_dict)

        # Sale Order Num 1
        po_dict = {
            'partner_id': self.partner.id,
        }
        self.sale_order_1 = self.sale_order_model.create(po_dict)
        uom_id = self.product_uom_model.search([
            ('name', '=', 'Unit(s)')])[0].id
        pr_dict = {
            'name': 'Product Test',
            'uom_id': uom_id,
            'sale_method': 'sale',
        }
        self.product = prod_model.sudo().create(pr_dict)
        pl_dict1 = {
            'date_planned': Datetime.now(),
            'name': 'PO01',
            'order_id': self.sale_order_1.id,
            'product_id': self.product.id,
            'product_uom': uom_id,
            'price_unit': 1.0,
            'product_uom_qty': 5.0,
            'account_analytic_id': self.analytic_account_1.id,
        }
        self.sale_order_line_1 = \
            sale_order_line_model.sudo().create(pl_dict1)
        self.sale_order_1.button_confirm()

        # Sale Order Num 2
        po_dict2 = {
            'partner_id': self.partner2.id,
        }
        self.sale_order_2 = self.sale_order_model.create(po_dict2)
        pr_dict2 = {
            'name': 'Product Test 2',
            'uom_id': uom_id,
            'sale_method': 'deliver',
        }
        self.product2 = prod_model.sudo().create(pr_dict2)
        pl_dict2 = {
            'date_planned': Datetime.now(),
            'name': 'PO02',
            'order_id': self.sale_order_2.id,
            'product_id': self.product2.id,
            'product_uom': uom_id,
            'price_unit': 1.0,
            'product_uom_qty': 5.0,
            'account_analytic_id': self.analytic_account_1.id,
        }
        self.sale_order_line_2 = \
            sale_order_line_model.sudo().create(pl_dict2)
        self.sale_order_2.button_confirm()

    def test_compute_qty_to_invoice_and_deliver(self):
        self.assertEqual(self.sale_order_line_1.qty_to_invoice, 5.0,
                         "Expected 5 as qty_to_invoice in the PO line")
        self.assertEqual(self.sale_order_line_1.qty_to_deliver, 5.0,
                         "Expected 5 as qty_to_deliver in the PO line")
        self.assertEqual(self.sale_order_1.qty_to_invoice, 5.0,
                         "Expected 5 as qty_to_invoice in the PO")
        self.assertEqual(self.sale_order_1.qty_to_deliver, 5.0,
                         "Expected 5 as qty_to_deliver in the PO")

        self.assertEqual(self.sale_order_line_2.qty_to_invoice, 0.0,
                         "Expected 0 as qty_to_invoice in the PO line")
        self.assertEqual(self.sale_order_line_2.qty_to_deliver, 5.0,
                         "Expected 5 as qty_to_deliver in the PO line")
        self.assertEqual(self.sale_order_2.qty_to_invoice, 0.0,
                         "Expected 0 as qty_to_invoice in the PO")
        self.assertEqual(self.sale_order_2.qty_to_deliver, 5.0,
                         "Expected 5 as qty_to_deliver in the PO")

        # Now we deliver the products
        for picking in self.sale_order_2.picking_ids:
            picking.force_assign()
            picking.move_lines.write({'quantity_done': 5.0})
            picking.button_validate()

        self.assertEqual(self.sale_order_line_2.qty_to_invoice, 5.0,
                         "Expected 5 as qty_to_invoice in the PO line")
        self.assertEqual(self.sale_order_line_2.qty_to_deliver, 0.0,
                         "Expected 0 as qty_to_deliver in the PO line")
        self.assertEqual(self.sale_order_2.qty_to_invoice, 5.0,
                         "Expected 5 as qty_to_invoice in the PO")
        self.assertEqual(self.sale_order_2.qty_to_deliver, 0.0,
                         "Expected 0 as qty_to_deliver in the PO")

    def test_search_qty_to_invoice_and_deliver(self):
        found = self.sale_order_model.search(
            ['|', ('qty_to_invoice', '>', 0.0), ('qty_to_deliver', '>', 0.0)])
        self.assertTrue(
            self.sale_order_1.id in found.ids,
            'Expected PO %s in POs %s' % (self.sale_order_1.id, found.ids))
