# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_order_lot_selection_exclude_pending_orders = fields.Boolean(
        related="company_id.sale_order_lot_selection_exclude_pending_orders",
        readonly=False,
    )
