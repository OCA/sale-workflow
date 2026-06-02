# Copyright 2026 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_to_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice To",
        company_dependent=False,
        domain="[('id', '!=', id)]",
        help="Another customer that is in charge of receiving and paying the "
        "invoices of this partner. When set, sales orders for this partner "
        "use this partner as the invoice address, so the due amounts are "
        "owed by it instead of by this partner.",
    )

    def _get_invoice_to_partner(self):
        """Return the partner that should receive the invoices.

        Falls back to the commercial partner's ``Invoice To`` when the
        contact itself has none, so a sub-contact ordering on behalf of its
        company inherits the company-level setting. Returns an empty
        recordset when no override is defined.
        """
        self.ensure_one()
        return (
            self.invoice_to_partner_id
            or self.commercial_partner_id.invoice_to_partner_id
        )
