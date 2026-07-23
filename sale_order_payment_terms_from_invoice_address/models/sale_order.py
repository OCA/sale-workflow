# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_invoice_id")
    def _compute_payment_term_id(self):
        res = super()._compute_payment_term_id()
        if self.env["ir.config_parameter"].get_param(
            "sale_order_payment_terms_from_invoice_address."
            "compute_so_payment_terms_from_partner_invoice"
        ):
            for order in self:
                order = order.with_company(order.company_id)
                order.payment_term_id = (
                    order.partner_invoice_id.property_payment_term_id
                )
        return res
