# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_line_field_block = fields.Many2one(
        related="company_id.sale_line_field_block",
        help="This field will be checked to block the Sale Order Lines "
        "if the quantity is not enough",
        readonly=False,
    )
    sale_line_block_allowed_groups = fields.Many2many(
        related="company_id.sale_line_block_allowed_groups",
        help="These groups will be able to bypass the block on the Sale Order Lines "
        "if the quantity is not enough",
        readonly=False,
    )
