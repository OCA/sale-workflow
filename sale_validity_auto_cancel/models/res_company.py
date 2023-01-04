# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_validity_auto_cancel_days = fields.Integer(
        string="Auto-cancel expired quotations after (days)",
        default=0,
        help="Quotations will be cancelled after the specified number of"
        " days since the expiration date.",
    )

    _sql_constraints = [
        (
            "sale_validity_auto_cancel_days_positive",
            "CHECK (sale_validity_auto_cancel_days >= 0)",
            "The value of the field 'Auto-cancel expired quotations after' "
            "must be positive or 0.",
        ),
    ]
