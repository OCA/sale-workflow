# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    coupon_program_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Coupon Program Partner",
    )

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if fields is None:
            fields = {}
        select_str = """ ,
            scp.partner_id as coupon_program_partner_id
        """
        from_clause += (
            "left join sale_coupon_program scp on (l.coupon_program_id = scp.id)"
        )
        fields.update({"coupon_program_partner_id": select_str})
        groupby += ", scp.partner_id"
        return super()._query(
            with_clause=with_clause,
            fields=fields,
            groupby=groupby,
            from_clause=from_clause,
        )
