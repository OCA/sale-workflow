# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    open_blanket_orders_editable = fields.Boolean(
        default=True,
        help="Make open Blanket Orders more editable.",
    )
