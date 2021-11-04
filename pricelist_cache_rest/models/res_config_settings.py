# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    pricelist_cache_auhorize_apikey_ids = fields.Many2many(
        "auth.api.key",
        related="company_id.pricelist_cache_auhorize_apikey_ids",
        readonly=False,
    )
