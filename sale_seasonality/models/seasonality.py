# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Seasonality(models.Model):
    _inherit = "seasonality"

    granularity = fields.Selection(
        [("date", "Date"), ("month", "Month"), ("year", "Year")],
        required=True,
        default="year",
    )
