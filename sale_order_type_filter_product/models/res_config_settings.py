# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_order_type_invalid_product_action = fields.Selection(
        related="company_id.sale_order_type_invalid_product_action",
        readonly=False,
    )
