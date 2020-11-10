# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):

    _inherit = "product.category"

    is_program_category = fields.Boolean()
    program_product_sale_ok = fields.Boolean()
    program_product_discount_fixed_amount = fields.Boolean()
    default_promotion_next_order_category = fields.Boolean(copy=False)

    @api.onchange("is_program_category")
    def _onchange_is_program_category(self):
        if not self.is_program_category:
            self.program_product_sale_ok = False
            self.program_product_discount_fixed_amount = False
            self.default_promotion_next_order_category = False
