# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_line_field_block = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field to compare quantities on Sale Order Lines",
        help="This field will be checked to block the Sale Order Lines "
        "if the quantity is not enough",
        domain=[
            ("model_id.model", "=", "sale.order.line"),
            (
                "name",
                "in",
                (
                    "free_qty_today",
                    "qty_available_today",
                    "virtual_available_at_date",
                ),
            ),
        ],
    )
    sale_line_block_allowed_groups = fields.Many2many(
        comodel_name="res.groups",
        string="Allowed Groups to bypass the block",
        help="These groups will be able to bypass the block on the Sale Order Lines "
        "if the quantity is not enough",
    )
