# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    property_account_discount_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Discount Account",
        domain="['&', ('deprecated', '=', False), ('company_id', '=' current_company_id)]",
        help="Keep this field empty to use the default value from the product category.",
    )

    def _get_product_accounts(self):
        res = super()._get_product_accounts()
        res["discount"] = (
            self.property_account_discount_id
            or self.categ_id.property_account_discount_categ_id
        )
        return res
