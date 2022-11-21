# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    deposit_taxes_id = fields.Many2many(default="")

    def _prepare_so_line(self, order, analytic_tag_ids, tax_ids, amount):
        ret = super()._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
        if self.advance_payment_method != "delivered":
            # override the tax_id on so line
            ret["tax_id"] = [(6, 0, self.deposit_taxes_id.ids)]
        return ret
