# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_term_id = fields.Many2one(
        compute="_compute_payment_term_id",
        inverse="_inverse_payment_term_id",
        readonly=False,
        store=True,
    )

    @api.depends("partner_id.property_payment_term_id", "team_id.team_payment_term_id")
    def _compute_payment_term_id(self):
        for rec in self:
            if rec.partner_id.property_payment_term_id:
                rec.payment_term_id = rec.partner_id.property_payment_term_id
            elif rec.team_id.team_payment_term_id:
                rec.payment_term_id = rec.team_id.team_payment_term_id
            else:
                rec.payment_term_id = False

    def _inverse_payment_term_id(self):
        return

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        # TODO: to remove in V16, will be useless.
        super().onchange_partner_id()
        if (
            self.team_id.team_payment_term_id
            and not self.partner_id.property_payment_term_id
        ):
            self.payment_term_id = self._compute_payment_term_id()
