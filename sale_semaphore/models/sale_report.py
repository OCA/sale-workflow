# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    semaphore = fields.Selection(
        [
            ("success", "🟢"),
            ("warning", "🟡"),
            ("danger", "🔴"),
        ],
    )

    def _select_sale(self, fields=None):
        if not fields:
            fields = {}
        fields["semaphore"] = ", l.semaphore as semaphore"
        return super()._select_sale(fields=fields)

    def _group_by_sale(self, groupby=""):
        groupby += ", l.semaphore"
        return super()._group_by_sale(groupby)
