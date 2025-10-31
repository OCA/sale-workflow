# Copyright 2025 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from itertools import groupby

from odoo.exceptions import (
    AccessError,
    UserError,
)
from odoo.fields import Command

from odoo.addons.sale.models.sale_order import SaleOrder


# flake8: noqa: C901
# flake8: noqa: E501
# flake8: noqa: E741
def post_load_hook():
    """Patch sale.order._create_invoices to skip Odoo's delta_amount correction
    when context contains 'skip_dp_final_fix'.
    """

    def _create_invoices_new(self, grouped=False, final=False, date=None):
        if not self.env["account.move"].has_access("create"):
            try:
                self.check_access("write")
            except AccessError:
                return self.env["account.move"]

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = (
            0  # Incremental sequencing to keep the lines order on the invoice.
        )
        for order in self:
            if order.partner_invoice_id.lang:
                order = order.with_context(lang=order.partner_invoice_id.lang)
            order = order.with_company(order.company_id)

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    # Create a dedicated section for the down payments
                    # (put at the end of the invoiceable_lines)
                    invoice_line_vals.append(
                        Command.create(
                            order._prepare_down_payment_section_line(
                                sequence=invoice_item_sequence
                            )
                        ),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1
                invoice_line_vals.append(
                    Command.create(
                        line._prepare_invoice_line(sequence=invoice_item_sequence)
                    ),
                )
                invoice_item_sequence += 1

            invoice_vals["invoice_line_ids"] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list and self._context.get(
            "raise_if_nothing_to_invoice", True
        ):
            raise UserError(self._nothing_to_invoice_error_message())

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ],
            )
            for _grouping_keys, invoices in groupby(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ],
            ):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals["invoice_line_ids"] += invoice_vals[
                            "invoice_line_ids"
                        ]
                    origins.add(invoice_vals["invoice_origin"])
                    payment_refs.add(invoice_vals["payment_reference"])
                    refs.add(invoice_vals["ref"])
                ref_invoice_vals.update(
                    {
                        "ref": ", ".join(refs)[:2000],
                        "invoice_origin": ", ".join(origins),
                        "payment_reference": len(payment_refs) == 1
                        and payment_refs.pop()
                        or False,
                    }
                )
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env["sale.order.line"]
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice["invoice_line_ids"]:
                    line[2]["sequence"] = SaleOrderLine._get_invoice_line_sequence(
                        new=sequence, old=line[2]["sequence"]
                    )
                    sequence += 1

        moves = self._create_account_invoices(invoice_vals_list, final)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final and (
            moves_to_switch := moves.sudo().filtered(lambda m: m.amount_total < 0)
        ):
            with self.env.protecting([moves._fields["team_id"]], moves_to_switch):
                moves_to_switch.action_switch_move_type()
                self.invoice_ids._set_reversed_entry(moves_to_switch)

        for move in moves:
            # HOOK: skip_dp_final_fix
            if self.down_payment_final_rounding(final):
                # END HOOK: skip_dp_final_fix
                # Downpayment might have been determined by a fixed amount set by the user.
                # This amount is tax included. This can lead to rounding issues.
                # E.g. a user wants a 100€ DP on a product with 21% tax.
                # 100 / 1.21 = 82.64, 82.64 * 1,21 = 99.99
                # This is already corrected by adding/removing the missing cents on the DP invoice,
                # but must also be accounted for on the final invoice.

                delta_amount = 0
                for order_line in self.order_line:
                    if not order_line.is_downpayment:
                        continue
                    inv_amt = order_amt = 0
                    for invoice_line in order_line.invoice_lines:
                        sign = 1 if invoice_line.move_id.is_inbound() else -1
                        if invoice_line.move_id == move:
                            inv_amt += invoice_line.price_total * sign
                        elif (
                            invoice_line.move_id.state != "cancel"
                        ):  # filter out canceled dp lines
                            order_amt += invoice_line.price_total * sign
                    if inv_amt and order_amt:
                        # if not inv_amt, this order line is not related to current move
                        # if no order_amt, dp order line was not invoiced
                        delta_amount += inv_amt + order_amt

                if not move.currency_id.is_zero(delta_amount):
                    receivable_line = move.line_ids.filtered(
                        lambda aml: aml.account_id.account_type == "asset_receivable"
                    )[:1]
                    product_lines = move.line_ids.filtered(
                        lambda aml: aml.display_type == "product" and aml.is_downpayment
                    )
                    tax_lines = move.line_ids.filtered(
                        lambda aml: aml.tax_line_id.amount_type not in (False, "fixed")
                    )
                    if tax_lines and product_lines and receivable_line:
                        line_commands = [
                            Command.update(
                                receivable_line.id,
                                {
                                    "amount_currency": receivable_line.amount_currency
                                    + delta_amount,
                                },
                            )
                        ]
                        delta_sign = 1 if delta_amount > 0 else -1
                        for lines, attr, sign in (
                            (
                                product_lines,
                                "price_total",
                                -1 if move.is_inbound() else 1,
                            ),
                            (tax_lines, "amount_currency", 1),
                        ):
                            remaining = delta_amount
                            lines_len = len(lines)
                            for line in lines:
                                if (
                                    move.currency_id.compare_amounts(remaining, 0)
                                    != delta_sign
                                ):
                                    break
                                amt = delta_sign * max(
                                    move.currency_id.rounding,
                                    abs(move.currency_id.round(remaining / lines_len)),
                                )
                                remaining -= amt
                                line_commands.append(
                                    Command.update(
                                        line.id, {attr: line[attr] + amt * sign}
                                    )
                                )
                        move.line_ids = line_commands

            move.message_post_with_source(
                "mail.message_origin_link",
                render_values={
                    "self": move,
                    "origin": move.line_ids.sale_line_ids.order_id,
                },
                subtype_xmlid="mail.mt_note",
            )
        return moves

    if not hasattr(SaleOrder, "_create_invoices_original"):
        SaleOrder._create_invoices_original = _create_invoices_new
    SaleOrder._create_invoices = _create_invoices_new
