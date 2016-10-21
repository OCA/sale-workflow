# -*- coding: utf-8 -*-
# Copyright 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase


class TestSaleOrderMerge(TransactionCase):
    def setUp(self):
        super(TestSaleOrderMerge, self).setUp()
        self.journal_sale = self.env.ref('account.sales_journal')
        self.env.ref('product.product_product_24').write({
            'list_price': 2,
        })
        self.env.ref('product.product_product_25').write({
            'list_price': 3,
        })
        self.period_id = self.env['account.period'].find().id

    def create_sale_orders(self, policy):
        order1 = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'order_policy': policy,
            'order_line': [
                (0, 0, {
                    'product_id': self.env.ref(
                        'product.product_product_24').id,
                    'product_uom_qty': 1,
                    }),
            ]
        })
        order2 = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'order_policy': policy,
            'order_line': [
                (0, 0, {
                    'product_id': self.env.ref(
                        'product.product_product_24').id,
                    'product_uom_qty': 1,
                    }),
                (0, 0, {
                    'product_id': self.env.ref(
                        'product.product_product_25').id,
                    'product_uom_qty': 1,
                    }),
            ]
        })
        return order1, order2

    def merge(self, order1, order2):
        """ Create a wizard, check that mergeable orders are added by default.
        Reset mergeable orders to only order2, excluding other orders from
        demo data. Perform the merge """
        wiz = self.env['sale.order.merge'].browse(
            order1.button_merge()['res_id'])
        self.assertIn(order2, wiz.to_merge)
        wiz.to_merge = order2
        wiz.merge()
        self.assertEqual(order2.state, 'cancel')

    def pay_invoice(self, invoice):
        """ Confirm and pay the invoice """
        invoice.signal_workflow('invoice_open')
        invoice.pay_and_reconcile(
            invoice.amount_total, self.env.ref('account.cash').id,
            self.period_id, self.env.ref('account.bank_journal').id,
            self.env.ref('account.cash').id,
            self.period_id, self.env.ref('account.bank_journal').id,)
        self.assertEqual(invoice.state, 'paid')

    def test_01_policy_manual(self):
        """ Check that state is manual after merging orders in different states
        because otherwise the button to create additional invoices is not
        visible.
        """
        order1, order2 = self.create_sale_orders('manual')
        order1.action_button_confirm()
        order2.action_button_confirm()
        self.assertEqual(order1.state, 'manual')
        order1.action_invoice_create()
        order1.signal_workflow('manual_invoice')
        invoice1 = order1.invoice_ids
        self.assertEqual(order1.state, 'progress')

        self.merge(order1, order2)
        self.assertEqual(order1.state, 'manual')

        # Pay first invoice
        self.pay_invoice(invoice1)
        self.assertLess(order1.invoiced_rate, 100)
        order1.action_invoice_create()
        order1.signal_workflow('manual_invoice')
        self.assertEqual(order1.state, 'progress')

        # Pay second invoice
        self.assertEqual(len(order1.invoice_ids), 2)
        invoice2 = order1.invoice_ids - invoice1
        self.pay_invoice(invoice2)
        self.assertEqual(order1.invoiced_rate, 100)

        picking1 = order1.picking_ids
        picking1.force_assign()
        picking1.do_prepare_partial()
        picking1.do_transfer()
        self.assertEqual(order1.state, 'done')

    def test_02_policy_prepaid(self):
        """ Merge prepaid orders and check procurment trigger """
        order1, order2 = self.create_sale_orders('prepaid')
        order1.action_button_confirm()
        order2.action_button_confirm()
        self.assertEqual(order1.amount_untaxed, 2)
        self.assertEqual(order1.state, 'progress')
        self.assertEqual(order2.state, 'progress')
        self.assertIn(order1, order2.merge_with)
        self.assertIn(order2, order1.merge_with)
        self.assertTrue(order1.merge_ok)
        self.assertTrue(order2.merge_ok)

        # Pay order1's invoice to trigger procurement
        invoice1 = order1.invoice_ids
        self.pay_invoice(invoice1)
        self.assertEqual(order1.invoiced_rate, 100)

        picking1 = order1.picking_ids
        self.assertEqual(len(picking1.move_lines), 1)

        self.merge(order1, order2)
        self.assertLess(order1.invoiced_rate, 100)

        # The procurement of the additional lines has been triggered
        self.assertEqual(len(picking1.move_lines), 3)

        # Deliver order and check order status
        picking1.force_assign()
        picking1.do_prepare_partial()
        picking1.do_transfer()
        self.assertEqual(order1.state, 'done')

    def test_03_policy_picking(self):
        """ Merge a partially delivered order into an undelivered one """
        order1, order2 = self.create_sale_orders('picking')
        order1.action_button_confirm()
        order2.action_button_confirm()
        self.assertEqual(order1.amount_untaxed, 2)
        self.assertEqual(order1.state, 'progress')
        self.assertEqual(order2.state, 'progress')
        self.assertIn(order1, order2.merge_with)
        self.assertIn(order2, order1.merge_with)
        self.assertTrue(order1.merge_ok)
        self.assertTrue(order2.merge_ok)
        move_line1 = order1.picking_ids.move_lines
        self.assertEqual(len(move_line1), 1)

        # Partially deliver order 2 before merging
        picking2 = order2.picking_ids[0]
        picking2.force_assign()
        picking2.do_prepare_partial()
        self.env['stock.pack.operation'].search([
            ('picking_id', '=', picking2.id),
            ('product_id', '=', self.env.ref(
                'product.product_product_24').id)]).unlink()
        picking2.do_transfer()
        invoice_id = picking2.with_context(
            inv_type='out_invoice').action_invoice_create(
                journal_id=self.journal_sale.id, group=False,
                type='out_invoice')[0]
        invoice2 = self.env['account.invoice'].browse(invoice_id)

        self.merge(order1, order2)

        self.assertIn(picking2, order1.picking_ids)
        self.assertEqual(picking2.origin, order1.name)
        self.assertIn(invoice2, order1.invoice_ids)
        self.assertEqual(len(order1.order_line), 3)
        self.assertEqual(order1.amount_untaxed, 7)

        # Retrieve the remaining picking from the original move line, as it may
        # have been merged in order2's back order (or the other way around)
        picking1 = move_line1.picking_id
        self.assertEqual(len(picking1.move_lines), 2)
        self.assertIn(picking1, order1.picking_ids)

        # Process the remaining goods from the combined order
        picking1.force_assign()
        picking1.do_prepare_partial()
        picking1.do_transfer()
        self.assertEqual(order1.state, 'done')
        invoice_id = picking1.with_context(
            inv_type='out_invoice').action_invoice_create(
                journal_id=self.journal_sale.id, group=False,
                type='out_invoice')[0]

        invoice1 = self.env['account.invoice'].browse(invoice_id)
        invoice1.signal_workflow('invoice_open')
        invoice2.signal_workflow('invoice_open')
        self.assertEqual(order1.invoiced_rate, 100)

    def test_04_order_policy(self):
        """ The order policy is propagated from the confirmed to the draft """
        order1, order2 = self.create_sale_orders('prepaid')
        order2.write({'order_policy': 'manual'})
        order2.action_button_confirm()
        self.merge(order1, order2)
        self.assertEqual(order1.order_policy, 'manual')
