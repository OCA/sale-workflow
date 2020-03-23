# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ast

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from ..hooks import uninstall_hook


class TestSaleIsolatedQuotation(TransactionCase):
    def test_quotation_convert_to_order(self):
        """
        - When quotation is converted to order
          - Status chagned to 'done'
          - New sale.order of order_sequence = True created
        - Quotation can refer to Order and Order can refer to Quotation
        """
        self.quotation.action_convert_to_order()
        self.assertEqual(self.quotation.state, "done")
        self.sale_order = self.quotation.order_id
        self.assertTrue(self.sale_order.order_sequence)
        self.assertEqual(self.sale_order.state, "draft")
        self.assertEqual(self.sale_order.partner_id, self.partner)
        self.assertEqual(self.sale_order.quote_id, self.quotation)
        with self.assertRaises(UserError):
            self.sale_order.action_convert_to_order()

    def test_uninstall_hook(self):
        """"Test uninstall_hook"""
        actions = [
            "sale.action_quotations_with_onboarding",
            "sale.action_orders",
        ]
        # Check context and domain in action before uninstall this module
        for action_id in actions:
            action = self.env.ref(action_id)
            ctx = ast.literal_eval(action.context)
            dom = ast.literal_eval(action.domain or "{}")
            self.assertTrue("order_sequence" in ctx)
            self.assertTrue("default_order_sequence" in ctx)
            self.assertTrue("order_sequence" in map(lambda l: l[0], dom))
        # Uninstall this module
        uninstall_hook(self.cr, self.registry)
        # Check context and domain in action after uninstall this module
        for action_id in actions:
            action = self.env.ref(action_id)
            ctx = ast.literal_eval(action.context)
            dom = ast.literal_eval(action.domain or "{}")
            self.assertTrue("order_sequence" not in ctx)
            self.assertTrue("default_order_sequence" not in ctx)
            self.assertTrue("order_sequence" not in map(lambda l: l[0], dom))
            if action_id == "sale.action_orders":
                self.assertTrue("state" in map(lambda l: l[0], dom))
            else:
                self.assertTrue("search_default_my_quotation" in ctx)

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_2")
        vals = {
            "partner_id": self.partner.id,
            "order_sequence": False,
        }
        self.quotation = self.env["sale.order"].create(vals)
