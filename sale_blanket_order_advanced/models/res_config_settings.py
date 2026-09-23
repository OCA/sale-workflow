# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_version_control = fields.Boolean(
        string="Enable Version Control by Default",
        default=False,
        config_parameter="sale_blanket_order_advanced.enable_version_control",
    )
    enable_product_costs = fields.Boolean(
        string="Enable Product Costs Tracking by Default",
        default=False,
        config_parameter="sale_blanket_order_advanced.enable_product_costs",
    )
    enable_service_costs = fields.Boolean(
        string="Enable Service Costs Tracking by Default",
        default=False,
        config_parameter="sale_blanket_order_advanced.enable_service_costs",
    )
    use_sale_order_plan = fields.Boolean(
        string="Enable Order Plan by Default",
        default=False,
        config_parameter="sale_blanket_order_advanced.use_sale_order_plan",
    )
