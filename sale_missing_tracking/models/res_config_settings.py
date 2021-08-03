# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_missing_max_delay_times = fields.Integer(
        related="company_id.sale_missing_max_delay_times", readonly=False
    )
    sale_missing_days_from = fields.Integer(
        related="company_id.sale_missing_days_from", readonly=False
    )
    sale_missing_days_to = fields.Integer(
        related="company_id.sale_missing_days_to", readonly=False
    )
    sale_missing_days_notification = fields.Integer(
        related="company_id.sale_missing_days_notification", readonly=False
    )
    sale_missing_months_consumption = fields.Integer(
        related="company_id.sale_missing_months_consumption", readonly=False
    )
    sale_missing_minimal_consumption = fields.Monetary(
        related="company_id.sale_missing_minimal_consumption",
        readonly=False,
    )
