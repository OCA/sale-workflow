# Copyright 2023 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _convert_to_order_currency(self, order_currency):
        self.ensure_one()
        return self.currency_id._convert(
            self.amount,
            order_currency,
            self.acquirer_id.company_id,
            self.date,
        )

    def _check_amount_and_confirm_order(self):
        # OVERRIDE: handle sale orders confirmations for orders with multiple
        # payment transactions linked to them
        self.ensure_one()
        orders = self.sale_order_ids.filtered(lambda so: so.state in ("draft", "sent"))
        for order in orders:
            # Confirm orders only if:
            # 1. they're linked to multiple transactions
            # 2. the SO total amount is lower than the sum of the transactions' amounts
            # ``super()`` will handle the workflow for every other case
            order_transactions = order.transaction_ids.filtered(
                lambda t: t.state in ("authorized", "done")
            )
            if self < order_transactions:
                order_currency = order.currency_id
                transactions_amount = sum(
                    t._convert_to_order_currency(order_currency)
                    for t in order_transactions
                )
                if (
                    order_currency.compare_amounts(
                        transactions_amount, order.amount_total
                    )
                    >= 0
                ):
                    order.with_context(send_email=True).action_confirm()
        # NB: we have now 2 scenarios:
        # 1. every order linked to the transaction has been confirmed
        #    -> calling ``super()`` will do nothing, because the original
        #    method handles only draft or sent orders
        # 2. some orders have not been confirmed because the transactions'
        # total amount was lower than the SO amount, or because they're linked
        # to a single transaction
        #    -> let the ``super()`` handle them
        return super()._check_amount_and_confirm_order()
