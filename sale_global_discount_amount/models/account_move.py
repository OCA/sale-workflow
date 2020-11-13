# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    global_discount_amount_readonly = fields.Boolean(
        string="Global Discount Amount Readonly"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals:
                for invoice_line in vals.get("invoice_line_ids", []):
                    if invoice_line[2].get("is_discount_line", False) and invoice_line[
                        2
                    ].get("sale_line_ids", False):
                        # for not create new discount lines
                        self = self.with_context(discount_lines_from_sale=True)
                        vals["global_discount_amount_readonly"] = True
                        break
        return super().create(vals_list)

    def write(self, vals):
        # can not unlink move lines with sale lines
        if self.invoice_line_ids.filtered(
            lambda x: x.is_discount_line and x.sale_line_ids
        ):
            self = self.with_context(discount_lines_from_sale=True)
        res = super().write(vals)
        return res
