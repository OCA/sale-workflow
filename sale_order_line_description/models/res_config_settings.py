# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_use_product_description_per_so_line = fields.Boolean(
        string="Allow using only the product sale description on the sales order "
        "lines",
        implied_group="sale_order_line_description."
        "group_use_product_description_per_so_line",
        help="Allows you to use only product sale description on the "
        "sales order line.",
    )
