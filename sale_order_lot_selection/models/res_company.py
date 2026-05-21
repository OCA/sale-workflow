# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    sale_order_lot_selection_exclude_pending_orders = fields.Boolean(
        string="Exclude pending orders from the lot selection",
        help="If this checkbox is selected, serials that can be selected with pending "
        "sales orders will be excluded",
        default=False,
    )
