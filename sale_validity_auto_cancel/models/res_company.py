# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_validity_auto_cancel_days = fields.Integer(
        string="Auto-cancel expired quotations after (days)",
        default=0,
        help="Quotations will be cancelled after the specified number of"
        " days since the expiration date.",
    )
    sale_validity_warning_days = fields.Integer(
        string="Default Validity Warning of Sale Orders",
        default=0,
        help="By default, the validity date warning of sale orders will be "
        "the number of days defined on this field before the date of the "
        "validity sale order. If the value of this field is 0, the sale orders "
        "will not have a validity warning by default.",
    )

    sale_validity_warning_enabled = fields.Boolean(default=False)

    _sql_constraints = [
        (
            "sale_validity_auto_cancel_days_positive",
            "CHECK (sale_validity_auto_cancel_days >= 0)",
            "The value of the field 'Auto-cancel expired quotations after' "
            "must be positive or 0.",
        ),
        (
            "sale_order_validity_warning_days_positive",
            "CHECK (sale_validity_warning_days >= 0)",
            "The value of the field 'Default Validity Warning of Sale Orders' "
            "must be positive or 0.",
        ),
    ]

    @api.constrains("sale_validity_warning_days", "sale_validity_auto_cancel_days")
    def _check_warning_vs_auto_cancel(self):
        for rec in self:
            if (
                rec.sale_validity_warning_days
                and rec.sale_validity_auto_cancel_days
                and rec.sale_validity_warning_days >= rec.sale_validity_auto_cancel_days
            ):
                raise ValidationError(
                    _(
                        "The 'Default Validity Warning of Sale Orders' must be less than "
                        "'Auto-cancel expired quotations after (days)'."
                    )
                )
