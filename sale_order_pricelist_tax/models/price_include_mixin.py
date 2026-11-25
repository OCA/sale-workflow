# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PriceIncludeTax(models.AbstractModel):
    _name = "price.include.tax.mixin"
    _description = "Price Include Tax Check Mixin"

    price_tax_state = fields.Selection(
        selection=[
            ("include", "Include"),
            ("exclude", "Exclude"),
            ("exception", "Exception"),
        ],
        string="Price tax state",
        compute="_compute_price_tax_state",
    )

    def _get_all_taxes(self):
        if self._name == "sale.order":
            return self.order_line.tax_id
        if self._name == "account.move":
            return self.invoice_line_ids.tax_ids

    def _compute_price_tax_state(self):
        for rec in self:
            taxes = rec._get_all_taxes()
            taxe_price_inc = set(taxes.mapped("price_include"))
            if len(taxe_price_inc) > 1:
                rec.price_tax_state = "exception"
            elif len(taxe_price_inc) == 1 and taxe_price_inc.pop():
                rec.price_tax_state = "include"
            else:
                rec.price_tax_state = "exclude"
