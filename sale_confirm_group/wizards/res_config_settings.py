# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Settings(models.TransientModel):
    _inherit = "res.config.settings"

    use_sale_confirmation_groups = fields.Boolean(
        related="company_id.use_sale_confirmation_groups",
        readonly=False,
    )
    sale_confirmation_group_ids = fields.Many2many(
        "res.groups",
        related="company_id.sale_confirmation_group_ids",
        readonly=False,
    )
