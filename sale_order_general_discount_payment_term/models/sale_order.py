# Copyright 2023 Nextev
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("payment_term_id")
    def _compute_general_discount(self):
        for so in self:
            if so.payment_term_id.sale_discount:
                so.general_discount = so.payment_term_id.sale_discount
            else:
                super()._compute_general_discount()
