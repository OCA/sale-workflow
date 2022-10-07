from itertools import groupby

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pdp_ids = fields.One2many("planned.down.payment", "order_id")
    pdp_total = fields.Float("DP Total", compute="_compute_pdp_total")

    def action_create_pdp(self):
        pdp_id = self.env["planned.down.payment"].create({"order_id": self.id})
        return {
            "name": _("Planned Down Payment"),
            "view_mode": "form",
            "views": [
                (self.env.ref("sale_product_advance_payment.pdp_view_form").id, "form")
            ],
            "res_model": "planned.down.payment",
            "res_id": pdp_id.id,
            "type": "ir.actions.act_window",
            "target": "current",
        }

    @api.depends("order_line.invoice_lines")
    def _get_invoiced(self):
        super(SaleOrder, self)._get_invoiced()
        self.pdp_ids._compute_invoice_id()

    def _compute_pdp_total(self):
        for rec in self:
            rec.pdp_total = sum(rec.pdp_ids.mapped("total"))

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
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
            order = order.with_company(order.company_id)
            order.env["sale.order.line"]

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
                        (
                            0,
                            0,
                            order._prepare_down_payment_section_line(
                                sequence=invoice_item_sequence,
                            ),
                        ),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1
                invoice_line_vals.append(
                    (
                        0,
                        0,
                        line._prepare_invoice_line(
                            sequence=invoice_item_sequence,
                        ),
                    ),
                )
                invoice_item_sequence += 1
                # Mod start
                pdpl = self.env["pdp.line"].search([("order_line_id", "=", line.id)])
                # TODO reduced should be computed based on linked moves
                if (
                    len(pdpl) == 1
                    and line.qty_to_invoice <= pdpl.qty - pdpl.qty_reduced
                ):
                    vals = (
                        0,
                        0,
                        {
                            "display_type": False,
                            "sequence": 2,
                            "name": "%s - Down Payment"
                            % pdpl.order_line_id.product_id.display_name,
                            "product_id": pdpl.pdp_id.get_dp_product().id,
                            "product_uom_id": 1,
                            "quantity": -line.qty_to_invoice,
                            "price_unit": pdpl.amount,
                            "tax_ids": [(6, 0, [])],
                            "analytic_account_id": False,
                            "analytic_tag_ids": [(6, 0, [])],
                        },
                    )
                    invoice_line_vals.append(vals)
                    pdpl.qty_reduced += line.qty_to_invoice
                    # Mod end
            invoice_vals["invoice_line_ids"] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise self._nothing_to_invoice_error()

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
            for grouping_keys, invoices in groupby(
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

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = (
            self.env["account.move"]
            .sudo()
            .with_context(default_move_type="out_invoice")
            .create(invoice_vals_list)
        )

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(
                lambda m: m.amount_total < 0
            ).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view(
                "mail.message_origin_link",
                values={
                    "self": move,
                    "origin": move.line_ids.mapped("sale_line_ids.order_id"),
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )
        return moves


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    dp_amount_invoiced = fields.Float("DP Invoiced", compute="_compute_pdp_values")
    dp_amount_remaining = fields.Float("DP Remaining", compute="_compute_pdp_values")
    pdp_line_id = fields.Many2one("pdp.line", string="PDP Line")

    def _compute_pdp_values(self):
        for rec in self:
            pdp_lines = self.env["pdp.line"].search(
                [("order_line_id", "=", rec.id), ("pdp_state", "=", "invoiced")]
            )
            rec.dp_amount_invoiced = sum(pdp_lines.mapped("total"))
            rec.dp_amount_remaining = rec.price_subtotal - rec.dp_amount_invoiced
