# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    pricelist_cache_by_date = fields.Boolean(
        related="company_id.pricelist_cache_by_date",
        readonly=False,
    )
