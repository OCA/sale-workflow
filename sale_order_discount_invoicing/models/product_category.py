# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_account_discount_categ_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Discount Account",
        domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used when validating a customer invoice.",
    )
