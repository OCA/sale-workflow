# Copyright 2022 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _stock_account_anglo_saxon_reconcile_valuation(self, product=False):
        super()._stock_account_anglo_saxon_reconcile_valuation(product=product)
        for move in self:
            if not move.is_invoice():
                continue
            if not move.company_id.anglo_saxon_accounting:
                continue

            stock_moves = move._stock_account_get_last_step_stock_moves()

            if not stock_moves:
                continue

            products = product or move.mapped("invoice_line_ids.product_id")
            for prod in products:
                if prod.valuation != "real_time":
                    continue
                # We first get the invoices move lines (taking the
                # invoice and the previous ones into account)...
                product_accounts = prod.product_tmpl_id._get_product_accounts()
                if move.is_sale_document():
                    product_interim_account = product_accounts["stock_output"]
                else:
                    product_interim_account = product_accounts["stock_input"]

                if product_interim_account.reconcile:
                    # Search for anglo-saxon lines linked to the product in the journal entry.
                    product_account_moves = move.line_ids.filtered(
                        lambda line: line.product_id == prod
                        and line.account_id == product_interim_account
                        and not line.reconciled
                    )
                    for sale_line in product_account_moves.mapped("sale_line_id"):
                        sl_product_account_moves = product_account_moves.filtered(
                            lambda x: sale_line in x.sale_line_id
                        )
                        # Search for anglo-saxon lines linked to
                        # the same sales order line in the stock moves.
                        product_stock_moves = stock_moves.filtered(
                            lambda stock_move: stock_move.sale_line_id == sale_line
                        )
                        sl_product_account_moves += product_stock_moves.mapped(
                            "account_move_ids.line_ids"
                        ).filtered(
                            lambda line: line.account_id == product_interim_account
                            and not line.reconciled
                        )
                        # Reconcile.
                        sl_product_account_moves.reconcile()
