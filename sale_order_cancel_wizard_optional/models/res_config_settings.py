# Copyright 2023 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    disable_sale_order_cancel_warning = fields.Boolean(
        related="company_id.disable_sale_order_cancel_warning",
        readonly=False,
    )
