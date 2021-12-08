# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_option_product = fields.Boolean(
        "Show optional products on Sale Orders",
        implied_group="sale_order_option_product_group.group_option_product",
    )
