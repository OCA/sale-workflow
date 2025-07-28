# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_exception_show_popup = fields.Boolean(
        string="Sale Exception Popup",
        default=True,
    )
