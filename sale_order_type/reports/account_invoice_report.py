# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Order Type",
    )

    def _select(self):
        return SQL("%s, move.sale_type_id as sale_type_id", super()._select())
