# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    coupon_program_id = fields.Many2one(
        comodel_name="sale.coupon.program", string="Coupon Program",
    )

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if fields is None:
            fields = {}
        select_str = """ ,
            l.coupon_program_id as coupon_program_id
        """
        fields.update({"coupon_program_id": select_str})
        groupby += ", l.coupon_program_id"
        return super()._query(
            with_clause=with_clause,
            fields=fields,
            groupby=groupby,
            from_clause=from_clause,
        )
