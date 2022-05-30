# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    team_payment_term_id = fields.Many2one(
        "account.payment.term",
        company_dependent=True,
        string="Payment term",
        domain="[('company_id', 'in', [current_company_id, False])]",
        help="This payment method will be used if none is indicated "
        "on the customer profil, and will apply on sale orders "
        "and invoices.",
    )
