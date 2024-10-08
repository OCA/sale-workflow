# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Type",
        store=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        copy=True,
    )

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if res.get("move_type") in ["out_invoice", "out_refund"]:
            res.update(
                {
                    "sale_type_id": self.env["sale.order.type"].search(
                        [("company_id", "in", [self.env.company.id, False])], limit=1
                    )
                }
            )
        return res

    @api.onchange("partner_id")
    def onchange_type_id(self):
        if self.move_type in ["out_invoice", "out_refund"]:
            sale_type = (
                self.partner_id.with_company(self.company_id).sale_type
                or self.partner_id.commercial_partner_id.with_company(
                    self.company_id
                ).sale_type
            )
            if sale_type:
                self.sale_type_id = sale_type
                self.onchange_sale_type_id()

    @api.onchange("sale_type_id")
    def onchange_sale_type_id(self):
        # TODO: To be changed to computed stored readonly=False if possible in v14?
        if self.sale_type_id.payment_term_id:
            self.invoice_payment_term_id = self.sale_type_id.payment_term_id.id
        if self.sale_type_id.journal_id:
            self.journal_id = self.sale_type_id.journal_id.id
