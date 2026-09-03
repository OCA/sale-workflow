# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        string="Lot",
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["lot_id"] = "l.lot_id"
        return res

    def _group_by_sale(self):
        group_by = super()._group_by_sale()
        group_by += ", l.lot_id"
        return group_by
