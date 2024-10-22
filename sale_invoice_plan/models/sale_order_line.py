# Copyright 2023 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models
from odoo.tools.float_utils import float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_installment_invoice_amount(self, percent):
        """Simulate the invoice lime amount, after applying a percentage to it"""
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        quantity = float_round(self.product_uom_qty * percent / 100, prec)
        invoice_amount = self.currency_id.round(self.price_unit * quantity)
        return invoice_amount
