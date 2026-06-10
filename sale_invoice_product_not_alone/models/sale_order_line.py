# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _can_be_invoiced_alone(self):
        return (
            super()._can_be_invoiced_alone() and not self.product_id.avoid_invoice_alone
        )
