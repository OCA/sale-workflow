# coding: utf-8
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSaleRevertDone(TransactionCase):
    def test_sale_revert_done(self):
        order = self.env.ref('sale.sale_order_4').copy()
        order.action_confirm()
        self.assertEqual(order.state, 'sale')
        order.action_done()
        self.assertEqual(order.state, 'done')
        order.action_revert_done()
        self.assertEqual(order.state, 'sale')
        with self.assertRaisesRegexp(ValidationError, 'not in state'):
            order.action_revert_done()
        order.action_done()
        self.assertEqual(order.state, 'done')
