# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    secondary_user_id = fields.Many2one(
        comodel_name="res.users", string="Secondary Salesperson"
    )

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        fields = fields or {}
        fields["secondary_user_id"] = ", s.secondary_user_id AS secondary_user_id"
        groupby += ", s.secondary_user_id"
        return super()._query(with_clause, fields, groupby, from_clause)
