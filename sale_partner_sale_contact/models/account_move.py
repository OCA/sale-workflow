# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = ["account.move", "sale.contact.mixin"]
    _name = "account.move"

    sale_contact_partner_id = fields.Many2one(
        # Not copied on duplication: the contact is normally propagated from
        # the sale order via _prepare_invoice().  Carrying it over on a manual
        # duplicate risks stale data (person has left, role changed, etc.).
        copy=False,
        help="Contact person for this invoice. "
        "Only child contacts of the partner can be selected.",
    )
