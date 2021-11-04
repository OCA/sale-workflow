# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    pricelist_cache_auhorize_apikey_ids = fields.Many2many(
        "auth.api.key",
        help="API keys that can retrieve pricelist data via REST endpoints.",
    )
