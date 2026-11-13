# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    sale_auto_update_delivery_address = fields.Boolean(
        string="Auto-update Delivery Address",
        compute="_compute_sale_auto_update_delivery_address",
        store=True,
        readonly=False,
        help="If checked, the transfers of this operation type that are not done "
        "or cancelled are automatically updated when the delivery address of "
        "their sales order is changed.",
    )

    @api.depends("code")
    def _compute_sale_auto_update_delivery_address(self):
        # Only consider outgoing and internal types, to not change the
        # partner of receipts, returns, dropships, etc.
        for picking_type in self:
            picking_type.sale_auto_update_delivery_address = picking_type.code in (
                "outgoing",
                "internal",
            )
