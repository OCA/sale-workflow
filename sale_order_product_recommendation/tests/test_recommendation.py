# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class RecommendationCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(RecommendationCase, cls).setUpClass()
        cls.camptocamp = cls.env.ref("base.res_partner_12")
        cls.product_12 = cls.env.ref('product.product_product_12')
        cls.product_10 = cls.env.ref('product.product_product_10')
        cls.product_20 = cls.env.ref('product.product_product_20')
        # Create old sale orders to have searchable history
        cls.env["sale.order"].create({
            "partner_id": cls.camptocamp.id,
            "state": "done",
            "order_line": [
                (0, 0, {
                    "product_id": cls.product_12.id,
                    "name": cls.product_12.name,
                    "qty_delivered": 25,
                }),
                (0, 0, {
                    "product_id": cls.product_10.id,
                    "name": cls.product_10.name,
                    "qty_delivered": 50,
                }),
                (0, 0, {
                    "product_id": cls.product_20.id,
                    "name": cls.product_20.name,
                    "qty_delivered": 100,
                }),
            ],
        })
        cls.env["sale.order"].create({
            "partner_id": cls.camptocamp.id,
            "state": "done",
            "order_line": [
                (0, 0, {
                    "product_id": cls.product_10.id,
                    "name": cls.product_10.name,
                    "qty_delivered": 50,
                }),
            ],
        })
        # Create a new sale order for the same customer
        cls.new_so = cls.env["sale.order"].create({
            "partner_id": cls.camptocamp.id,
        })

    def wizard(self):
        """Get a wizard."""
        wizard = self.env["sale.order.recommendation"] \
            .with_context(active_id=self.new_so.id) \
            .create({})
        wizard._generate_recommendations()
        return wizard

    def test_recommendations(self):
        """Recommendations are OK."""
        self.new_so.order_line = [(0, 0, {
            "product_id": self.product_12.id,
            "product_uom_qty": 3,
        })]
        self.new_so.order_line.product_id_change()
        wizard = self.wizard()
        # Order came in from context
        self.assertEqual(wizard.order_id, self.new_so)
        # Product 12 is first recommendation because it's in the SO already
        self.assertEqual(wizard.line_ids[0].product_id, self.product_12)
        self.assertEqual(wizard.line_ids[0].times_delivered, 2)
        self.assertEqual(wizard.line_ids[0].units_delivered, 25)
        self.assertEqual(wizard.line_ids[0].units_included, 3)
        # Product 46 appears second
        self.assertEqual(wizard.line_ids[1].product_id, self.product_10)
        self.assertEqual(wizard.line_ids[1].times_delivered, 2)
        self.assertEqual(wizard.line_ids[1].units_delivered, 100)
        self.assertEqual(wizard.line_ids[1].units_included, 0)
        # Product 57 appears third
        self.assertEqual(wizard.line_ids[2].product_id, self.product_20)
        self.assertEqual(wizard.line_ids[2].times_delivered, 1)
        self.assertEqual(wizard.line_ids[2].units_delivered, 100)
        self.assertEqual(wizard.line_ids[2].units_included, 0)
        # Only 1 product if limited as such
        wizard.line_amount = 1
        wizard._generate_recommendations()
        self.assertEqual(len(wizard.line_ids), 2)

    def test_transfer(self):
        """Products get transferred to SO."""
        qty = 10
        wizard = self.wizard()
        wizard.line_ids[2].units_included = qty
        wizard.line_ids[2]._onchange_units_included()
        wizard.action_accept()
        self.assertEqual(len(self.new_so.order_line), 1)
        self.assertEqual(self.new_so.order_line.product_id, self.product_12)
        self.assertEqual(self.new_so.order_line.product_uom_qty, qty)
        # No we confirm the SO
        self.new_so.action_confirm()
        wizard = self.wizard()
        wiz_line = wizard.line_ids.filtered(
            lambda x: x.product_id == self.product_12)
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
            lambda x: x.product_id == self.product_12)
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
