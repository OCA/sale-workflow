# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from itertools import groupby

from odoo import api, models
from odoo.exceptions import AccessError, UserError
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_invoice_group_key(self, order):
        return (order.partner_invoice_id.id, order.currency_id.id)

    @api.model
    def _get_invoice_group_line_key(self, line):
        return self._get_invoice_group_key(line.order_id)

    @api.model
    def _get_draft_invoices(self, invoices_vals):
        return False

    @api.model
    def _modify_invoices(self, invoices):
        return invoices

    def _register_hook(self):  # noqa
        def new_create_invoices(self, grouped=False, final=False, date=None):
            """Create invoice(s) for the given Sales Order(s).

            :param bool grouped: if True, invoices are grouped by SO id.
                If False, invoices are grouped by keys returned by :meth:`_get_invoice_grouping_keys`
            :param bool final: if True, refunds will be generated if necessary
            :param date: unused parameter
            :returns: created invoices
            :rtype: `account.move` recordset
            :raises: UserError if one of the orders has no invoiceable lines.
            """  # noqa
            if not self.env["account.move"].check_access_rights("create", False):
                try:
                    self.check_access_rights("write")
                    self.check_access_rule("write")
                except AccessError:
                    return self.env["account.move"]

            # 1) Create invoices.
            invoice_vals_list = []
            invoice_item_sequence = (
                0  # Incremental sequencing to keep the lines order on the invoice.
            )
            for order in self:
                order = order.with_company(order.company_id).with_context(
                    lang=order.partner_invoice_id.lang
                )

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
                            )
                        )
                        down_payment_section_added = True
                        invoice_item_sequence += 1
                    invoice_line_vals.append(
                        Command.create(
                            line._prepare_invoice_line(sequence=invoice_item_sequence)
                        )
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
            if len(invoice_vals_list) < len(self):
                SaleOrderLine = self.env["sale.order.line"]
                for invoice in invoice_vals_list:
                    sequence = 1
                    for line in invoice["invoice_line_ids"]:
                        line[2]["sequence"] = SaleOrderLine._get_invoice_line_sequence(
                            new=sequence, old=line[2]["sequence"]
                        )
                        sequence += 1

            moves_to_create = []
            for inv_vals in invoice_vals_list:
                draft_inv = self._get_draft_invoices(inv_vals)
                if draft_inv:
                    draft_inv.update(inv_vals)

                    if final:
                        draft_inv.sudo().filtered(
                            lambda m: m.amount_total < 0
                        ).action_switch_invoice_into_refund_credit_note()

                    draft_inv.message_post_with_view(
                        "mail.message_origin_link",
                        values={
                            "self": draft_inv,
                            "origin": draft_inv.line_ids.sale_line_ids.order_id,
                        },
                        subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                            "mail.mt_note"
                        ),
                    )
                else:
                    moves_to_create.append(inv_vals)

            moves = (
                self.env["account.move"]
                .sudo()
                .with_context(default_move_type="out_invoice")
                .create(moves_to_create)
            )

            # 4) Some moves might actually be refunds: convert them if the total amount is negative # noqa
            if final:
                moves.sudo().filtered(
                    lambda m: m.amount_total < 0
                ).action_switch_invoice_into_refund_credit_note()
            for move in moves:
                move.message_post_with_view(
                    "mail.message_origin_link",
                    values={
                        "self": move,
                        "origin": move.line_ids.sale_line_ids.order_id,
                    },
                    subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                )
            return moves

        self._patch_method("_create_invoices", new_create_invoices)

        return super(SaleOrder, self)._register_hook()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice(self):
        return self.order_id._prepare_invoice()

    def _do_not_invoice(self):
        return False
