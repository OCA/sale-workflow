# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    sale_type_id = fields.Many2one(
        comodel_name='sale.order.type',
        string='Sale Order Type',
    )

    def _select(self):
        select_str = super()._select()
        select_str += """
            , sub.sale_type_id as sale_type_id
            """
        return select_str

    def _sub_select(self):
        select_str = super()._sub_select()
        select_str += """
            , ai.sale_type_id
            """
        return select_str

    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ", ai.sale_type_id"
        return group_by_str
