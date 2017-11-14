# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    sale_merge_draft_invoice = fields.Boolean(
        string="Invoices",
    )
