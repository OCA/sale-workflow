# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMassConfirm(TransactionCase):

    def setUp(self):
        super(TestMassConfirm, self).setUp()

        self.so = self.env['sale.order'].create({
            'partner_id': self.ref('base.res_partner_2'),
        })

    def test_mass_confirm_wizard(self):
        """
        Check for state after confirming several sale orders at once
        """
        sos = self.so + self.so.copy()
        wiz = self.env['sale.order.confirm.wizard'].with_context(
            active_ids=sos.ids).new()
        wiz.confirm_sale_orders()
        self.assertEqual(set(['sale']), set(sos.mapped('state')))
