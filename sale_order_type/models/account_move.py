# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Type",
        compute="_compute_sale_type_id",
        store=True,
        readonly=False,
        states={"posted": [("readonly", True)], "cancel": [("readonly", True)]},
    )

    @api.depends("partner_id", "company_id")
    def _compute_sale_type_id(self):
        self.sale_type_id = self.env["sale.order.type"]
        for record in self.filtered(
            lambda am: am.type in ["out_invoice", "out_refund"]
        ):
            if not record.partner_id:
                record.sale_type_id = self.env["sale.order.type"].search([], limit=1)
            else:
                sale_type = (
                    record.partner_id.with_context(
                        force_company=record.company_id.id
                    ).sale_type
                    or record.partner_id.commercial_partner_id.with_context(
                        force_company=record.company_id.id
                    ).sale_type
                )
                if sale_type:
                    record.sale_type_id = sale_type

    @api.onchange("sale_type_id")
    def onchange_sale_type_id(self):
        # TODO: To be changed to computed stored readonly=False if possible in v14?
        if self.sale_type_id.payment_term_id:
            self.invoice_payment_term_id = self.sale_type_id.payment_term_id.id
        if self.sale_type_id.journal_id:
            self.journal_id = self.sale_type_id.journal_id.id
