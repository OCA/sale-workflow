# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    last_delivery_date = fields.Datetime(
        string="Last delivery date",
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["last_delivery_date"] = "l.last_delivery_date"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ", l.last_delivery_date"
        return res
