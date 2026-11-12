# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class InvoiceBlockingReason(models.Model):
    _name = "invoice.blocking.reason"
    _description = "Sale invoice blocking reason"

    name = fields.Char(string="Reason", required=True)

    _name_uniq = models.Constraint(
        "unique (name)",
        "You cannot have two invoice blocking reasons with the same name.",
    )
