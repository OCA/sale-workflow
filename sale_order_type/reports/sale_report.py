# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    type_id = fields.Many2one(comodel_name="sale.order.type")

    def _select_dict(self, table):
        return super()._select_dict(table) | {"type_id": table.order_id.type_id}
