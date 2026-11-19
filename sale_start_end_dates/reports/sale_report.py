# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    start_date = fields.Date(readonly=True)
    end_date = fields.Date(readonly=True)
    number_of_days = fields.Integer(readonly=True)

    def _select_dict(self, table):
        return super()._select_dict(table) | {
            "start_date": table.start_date,
            "end_date": table.end_date,
            "number_of_days": table.number_of_days,
        }

    def _groupby_list(self, table):
        return super()._groupby_list(table) + [
            table.start_date,
            table.end_date,
            table.number_of_days,
        ]
