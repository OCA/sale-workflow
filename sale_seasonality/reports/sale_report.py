# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    seasonality_id = fields.Many2one("seasonality", string="Seasonality")

    def _select_sale(self):
        res = super()._select_sale()
        res += ", campaign.seasonality_id AS seasonality_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ", campaign.seasonality_id"
        return res

    def _from_sale(self):
        result = super()._from_sale()
        return f"""
            {result}
            LEFT JOIN utm_campaign campaign ON s.campaign_id = campaign.id
        """
