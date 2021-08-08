# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Type",
    )

    # flake8: noqa
    # pylint:disable=dangerous-default-value
    def _query(self, with_clause="", fields={}, groupby="", from_clause=""):
        fields["type_id"] = ", s.type_id as type_id"
        groupby += ", s.type_id"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
