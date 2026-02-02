# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoice_grouping_keys(self):
        res = super()._get_invoice_grouping_keys()
        if "invoice_payment_term_id" not in res:
            res.append("invoice_payment_term_id")

        return res
