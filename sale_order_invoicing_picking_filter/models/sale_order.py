# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import api, models
from odoo.exceptions import UserError
from odoo.fields import Command


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def invoice_picking_group(self, vals):
        new_invoice_vals_list = []
        invoice_grouping_keys = self._get_invoice_grouping_keys()
        vals = sorted(
            vals,
            key=lambda x: [
                x.get(grouping_key) for grouping_key in invoice_grouping_keys
            ],
        )
        for _grouping_keys, invoices in groupby(
            vals,
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
        return new_invoice_vals_list

    def _invoice_from_picking_services(self, order, outgoing_invoice_vals_list):
        service_lines = order.mapped("order_line").filtered(
            lambda x: x.invoice_status == "to invoice"
            and x.product_id.detailed_type == "service"
        )
        service_invoice_line_vals = []
        for line in service_lines:
            service_invoice_line_vals.append(
                Command.create(line._prepare_invoice_line()),
            )
        if service_invoice_line_vals and outgoing_invoice_vals_list:
            outgoing_invoice_vals_list[0][
                "invoice_line_ids"
            ] += service_invoice_line_vals
        elif service_invoice_line_vals:
            invoice_vals = order._prepare_invoice()
            invoice_vals["invoice_line_ids"] = service_invoice_line_vals
            outgoing_invoice_vals_list.append(invoice_vals)

    def _create_invoices_from_pickings(self, pickings):
        outgoing_invoice_vals_list = []
        incoming_invoice_vals_list = []
        for order in self:
            for code in ["outgoing", "incoming"]:
                move_ids = (
                    pickings.filtered(
                        lambda a: a.sale_id == order and a.picking_type_code == code
                    )
                    .mapped("move_ids")
                    .filtered("sale_line_id")
                )
                if move_ids:
                    invoice_vals = order._prepare_invoice()
                    invoice_line_vals = []
                    for move in move_ids:
                        invoice_line_vals.append(
                            Command.create(
                                move.sale_line_id._prepare_stock_move_invoice_line(move)
                            ),
                        )
                    invoice_vals["invoice_line_ids"] += invoice_line_vals
                    if code == "outgoing":
                        outgoing_invoice_vals_list.append(invoice_vals)
                    elif code == "incoming":
                        incoming_invoice_vals_list.append(invoice_vals)

            if self.env.context.get("invoice_service_products", False):
                self._invoice_from_picking_services(order, outgoing_invoice_vals_list)

        if not (
            outgoing_invoice_vals_list or incoming_invoice_vals_list
        ) and self._context.get("raise_if_nothing_to_invoice", True):
            raise UserError(self._nothing_to_invoice_error_message())

        if outgoing_invoice_vals_list:
            outgoing_invoice_vals_list = self.invoice_picking_group(
                outgoing_invoice_vals_list
            )
        if incoming_invoice_vals_list:
            incoming_invoice_vals_list = self.invoice_picking_group(
                incoming_invoice_vals_list
            )

        moves = self.env["account.move"]
        if outgoing_invoice_vals_list:
            moves += self.env["account.move"].sudo().create(outgoing_invoice_vals_list)
        if incoming_invoice_vals_list:
            for invoice in incoming_invoice_vals_list:
                invoice["move_type"] = "out_refund"
            moves += self.env["account.move"].sudo().create(incoming_invoice_vals_list)

        for move in moves:
            move.message_post_with_view(
                "mail.message_origin_link",
                values={"self": move, "origin": move.line_ids.sale_line_ids.order_id},
                subtype_id=self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_note"),
            )
        return moves
