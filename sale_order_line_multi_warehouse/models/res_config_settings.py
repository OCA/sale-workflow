# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_sale_multi_warehouse = fields.Boolean(
        related="company_id.allow_sale_multi_warehouse",
        string="Multi Warehouse in Sale Orders",
        readonly=False,
    )
