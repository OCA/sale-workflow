# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_commitment_date_required = fields.Boolean(
        "Delivery commitment date mandatory", default=False
    )
