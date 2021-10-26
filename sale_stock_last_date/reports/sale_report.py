# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    last_delivery_date = fields.Datetime(string="Last delivery date",)

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        fields = fields or {}
        fields["last_delivery_date"] = ", l.last_delivery_date AS" " last_delivery_date"
        groupby += ", l.last_delivery_date"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
