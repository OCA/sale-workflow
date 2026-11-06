# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

_PARAM_SET_FROM_PRODUCTS = "sale_order_team_from_product.set_team_from_products"
_PARAM_SKIP_IF_SET = "sale_order_team_from_product.skip_if_team_set"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    set_sales_team_from_products = fields.Boolean(
        help=(
            "If enabled, the Sales Team on a quotation will be set based on "
            "the Sales Team defined on the products."
        ),
        config_parameter=_PARAM_SET_FROM_PRODUCTS,
    )

    skip_sales_team_if_set = fields.Boolean(
        string="Skip if team is already set",
        help=(
            "If enabled, the Sales Team from products will not override an "
            "already set Sales Team on the quotation."
        ),
        config_parameter=_PARAM_SKIP_IF_SET,
    )
