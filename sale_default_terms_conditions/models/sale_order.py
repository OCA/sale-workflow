# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import is_html_empty


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.depends("partner_id")
    def _compute_note(self):
        res = super()._compute_note()
        for order in self:
            if not is_html_empty(order.partner_id.sale_order_note):
                order.note = order.partner_id.sale_order_note
        return res
