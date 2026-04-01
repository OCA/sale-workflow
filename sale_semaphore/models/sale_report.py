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

    def _select_additional_fields(self):
        fields = super()._select_additional_fields()
        fields["semaphore"] = "l.semaphore"
        return fields

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ", l.semaphore"
        return res
