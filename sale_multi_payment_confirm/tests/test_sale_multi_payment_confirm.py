# Copyright 2023 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import tests

from odoo.addons.sale.tests.test_sale_transaction import TestSaleTransaction


@tests.tagged("post_install", "-at_install")
class TestSaleTransaction(TestSaleTransaction):
    def test_00_sale_multi_payment_confirm(self):
        self.transaction.amount -= 10
        self.transaction2 = self.transaction.copy(
            {
                "amount": 10,
                "sale_order_ids": [(6, 0, self.transaction.sale_order_ids.ids)],
                "reference": (self.transaction.reference or "") + "COPY",
            }
        )
        transactions = self.transaction + self.transaction2
        transactions._set_transaction_done()
        transactions._post_process_after_done()
        self.assertEqual(self.order.state, "sale")
