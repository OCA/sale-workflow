# -*- coding: utf-8 -*-
# from datetime import date, timedelta
from odoo.tests.common import TransactionCase


class TestPaymentSignal(TransactionCase):

    def test_create(self):
        """Create a simple payment signal"""

        partner = self.env['res.partner'].create({
            'name': 'TEST',
            'customer': True,
        })

        payment_signal = self.env['sale.order'].create(
            {'partner_id': partner.id}
        )

        payment_signal._pay_signal()
