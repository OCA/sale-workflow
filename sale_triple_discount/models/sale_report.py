# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    discount2 = fields.Float("Discount 2 %", readonly=True)
    discount3 = fields.Float("Discount 3 %", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["discount2"] = "l.discount2"
        res["discount3"] = "l.discount3"
        return res

    @api.model
    def _group_by_sale(self):
        original_vals = super()._group_by_sale()

        additional_vals = """
            , l.discount2,
            l.discount3
        """

        return original_vals + additional_vals
