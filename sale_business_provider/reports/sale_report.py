# © 2021 Akretion (Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    business_provider_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if fields is None:
            fields = {}
        select_str = """ ,
            s.business_provider_id as business_provider_id
        """
        fields.update(
            {
                "business_provider_id": select_str,
            }
        )
        groupby += """,
            s.business_provider_id
        """
        return super()._query(
            with_clause=with_clause,
            fields=fields,
            groupby=groupby,
            from_clause=from_clause,
        )
