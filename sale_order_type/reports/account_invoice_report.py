# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Sale Order Type",
    )

    def _select_list(self, table):
        return super()._select_list(table) + [table.move_id.sale_type_id]
