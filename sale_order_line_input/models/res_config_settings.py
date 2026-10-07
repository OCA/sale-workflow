# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_view_sale_order_line = fields.Boolean(
        string="Enable Smart Button to view SO line right on SO Form",
        config_parameter="sale_order_line_input.show_view_sale_order_line",
        implied_group="sale_order_line_input.sale_orderline_view_group",
        group="sales_team.group_sale_salesman",
    )
