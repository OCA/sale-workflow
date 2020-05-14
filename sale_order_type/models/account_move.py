# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Type",
        compute="_compute_sale_type_id",
        readonly=False,
        store=True,
    )
    invoice_payment_term_id = fields.Many2one(
        compute="_compute_invoice_payment_term_id", store=True, readonly=False,
    )
    journal_id = fields.Many2one(
        compute="_compute_journal_id", store=True, readonly=False,
    )

    @api.depends("partner_id", "company_id")
    def _compute_sale_type_id(self):
        for record in self:
            if not record.is_invoice():
                continue
            if not record.partner_id:
                record.sale_type_id = self.env["sale.order.type"].search([], limit=1)
            else:
                sale_type = (
                    record.partner_id.with_context(
                        force_company=record.company_id.id
                    ).sale_type
                    or self.partner_id.commercial_partner_id.with_context(
                        force_company=record.company_id.id
                    ).sale_type
                )
                if sale_type:
                    record.sale_type_id = sale_type

    @api.depends("sale_type_id")
    def _compute_invoice_payment_term_id(self):
        if hasattr(super(), "_compute_invoice_payment_term_id"):
            super()._compute_invoice_payment_term_id()
        for rec in self:
            if rec.sale_type_id:
                rec.invoice_payment_term_id = rec.sale_type_id.payment_term_id

    @api.depends("sale_type_id")
    def _compute_journal_id(self):
        if hasattr(super(), "_compute_journal_id"):
            super()._compute_journal_id()
        for rec in self:
            if rec.sale_type_id.journal_id:
                rec.journal_id = rec.sale_type_id.journal_id
