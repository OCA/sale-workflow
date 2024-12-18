# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    start_date = fields.Date(readonly=True)
    end_date = fields.Date(readonly=True)
    number_of_days = fields.Integer(readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["start_date"] = "l.start_date"
        res["end_date"] = "l.end_date"
        res["number_of_days"] = "l.number_of_days"
        return res

    def _group_by_sale(self):
        sql = super()._group_by_sale()
        sql = f"{sql}, l.start_date, l.end_date, l.number_of_days"
        return sql
