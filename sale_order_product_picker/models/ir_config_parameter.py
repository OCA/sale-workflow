# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def get_picker_delay(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_picker.delay", default="1")
        )
