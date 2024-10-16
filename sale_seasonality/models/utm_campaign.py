# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class UtmCampaign(models.Model):
    _inherit = "utm.campaign"

    seasonality_id = fields.Many2one("seasonality", string="Seasonality")
    display_name = fields.Char(compute="_compute_display_name")
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    start_date_year = fields.Integer(compute="_compute_start_date_year", store=True)
    display_seasonality_name = fields.Char(
        compute="_compute_display_seasonality", store=True
    )

    @api.depends("start_date")
    def _compute_start_date_year(self):
        for rec in self:
            if not rec.start_date:
                rec.start_date_year = False
            else:
                rec.start_date_year = rec.start_date.year

    @api.depends("seasonality_id.name", "start_date_year")
    def _compute_display_seasonality(self):
        for rec in self:
            if rec.seasonality_id.granularity == "year" and rec.start_date_year:
                rec.display_seasonality_name = (
                    rec.seasonality_id.name + f" {rec.start_date_year}"
                )
            else:
                rec.display_seasonality_name = rec.seasonality_id.name

    def _compute_display_name(self):
        for rec in self:
            if rec.seasonality_id:
                rec.display_name = f"[{rec.display_seasonality_name}] {rec.name}"
            else:
                rec.display_name = rec.name
