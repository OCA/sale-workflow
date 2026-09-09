# Copyright 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    merge_order_confirm = fields.Boolean(
        default=False, config_parameter="sale_order_merge.merge_order_confirm"
    )
