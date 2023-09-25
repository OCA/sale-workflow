# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("delivery_state")
    def _get_invoice_status(self):
        super()._get_invoice_status()
        for sale in self:
            if (
                sale.invoice_status == "to invoice"
                and sale.partner_id.invoice_policy == "fully"
                and sale.delivery_state != "done"
            ):
                sale.invoice_status = "no"
