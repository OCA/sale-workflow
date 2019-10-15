# Copyright 2017 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .test_recommendation_common import RecommendationCase
from odoo.exceptions import UserError


class RecommendationCaseTests(RecommendationCase):

    def test_recommendations(self):
        """Recommendations are OK."""
        self.new_so.order_line = [(0, 0, {
            "product_id": self.prod_1.id,
            "product_uom_qty": 3,
            "qty_delivered_method": "manual",
        })]
        self.new_so.order_line.product_id_change()
        wizard = self.wizard()
        # Order came in from context
        self.assertEqual(wizard.order_id, self.new_so)
        self.assertEqual(len(wizard.line_ids), 3)
        # Product 1 is first recommendation because it's in the SO already
        self.assertEqual(wizard.line_ids[0].product_id, self.prod_1)
        self.assertEqual(wizard.line_ids[0].times_delivered, 1)
        self.assertEqual(wizard.line_ids[0].units_delivered, 25)
        self.assertEqual(wizard.line_ids[0].units_included, 3)
        # Product 2 appears second
        wiz_line_prod2 = wizard.line_ids.filtered(
            lambda x: x.product_id == self.prod_2)
        self.assertEqual(wiz_line_prod2.times_delivered, 2)
        self.assertEqual(wiz_line_prod2.units_delivered, 100)
        self.assertEqual(wiz_line_prod2.units_included, 0)
        # Product 3 appears third
        wiz_line_prod3 = wizard.line_ids.filtered(
            lambda x: x.product_id == self.prod_3)
        self.assertEqual(wiz_line_prod3.times_delivered, 1)
        self.assertEqual(wiz_line_prod3.units_delivered, 100)
        self.assertEqual(wiz_line_prod3.units_included, 0)
        # Only 1 product if limited as such
        wizard.line_amount = 1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 2)

    def test_recommendations_archived_product(self):
        self.env["sale.order"].create({
            "partner_id": self.partner.id,
        })
        self.prod_1.active = False
        self.prod_2.sale_ok = False
        wizard = self.wizard()
        wizard._generate_recommendations()
        self.assertNotIn(self.prod_1, wizard.line_ids.mapped('product_id'))
        self.assertNotIn(self.prod_2, wizard.line_ids.mapped('product_id'))

    def test_transfer(self):
        """Products get transferred to SO."""
        qty = 10
        wizard = self.wizard()
        wiz_line_prod1 = wizard.line_ids.filtered(
            lambda x: x.product_id == self.prod_1)
        wiz_line_prod1.units_included = qty
        wiz_line_prod1._onchange_units_included()
        wizard.action_accept()
        self.assertEqual(len(self.new_so.order_line), 1)
        self.assertEqual(self.new_so.order_line.product_id, self.prod_1)
        self.assertEqual(self.new_so.order_line.product_uom_qty, qty)
        # No we confirm the SO
        self.new_so.action_confirm()
        wizard = self.wizard()
        wiz_line = wizard.line_ids.filtered(
            lambda x: x.product_id == self.prod_1)
        wiz_line.units_included = 0
        wiz_line._onchange_units_included()
        # The confirmed line can't be deleted
        with self.assertRaises(UserError):
            wizard.action_accept()
        # Deliver items and invoice the order
        self.new_so.order_line.qty_delivered = qty
        adv_wiz = self.env['sale.advance.payment.inv'].with_context(
            active_ids=[self.new_so.id]).create({
                'advance_payment_method': 'all',
            })
        adv_wiz.with_context(open_invoices=True).create_invoices()
        self.new_so.invoice_ids.action_invoice_open()
        # Open the wizard and add more product qty
        wizard = self.wizard()
        wiz_line = wizard.line_ids.filtered(
            lambda x: x.product_id == self.prod_1)
        wiz_line.units_included = qty + 2
        wiz_line._onchange_units_included()
        wizard.action_accept()
        # Deliver extra qty and make a new invoice
        self.new_so.order_line.qty_delivered = qty + 2
        adv_wiz = self.env['sale.advance.payment.inv'].with_context(
            active_ids=[self.new_so.id]).create({
                'advance_payment_method': 'all',
            })
        adv_wiz.with_context(open_invoices=True).create_invoices()
        self.assertEqual(2, len(self.new_so.invoice_ids))
        self.assertEqual(2,
                         self.new_so.invoice_ids[:1].invoice_line_ids.quantity)
