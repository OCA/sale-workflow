# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    customer_note = fields.Text(
        string="Customer Comments",
        compute="_compute_picking_notes",
        store=True,
        readonly=False,
    )
    note = fields.Html(
        compute="_compute_picking_notes",
        store=True,
        readonly=False,
    )

    @api.depends(
        "sale_id",
        "partner_id",
        "picking_type_id",
    )
    def _compute_picking_notes(self):
        for picking in self:
            if picking.picking_type_id.code != "incoming":
                picking.note = (
                    picking.sale_id.picking_note or picking.partner_id.picking_note
                )
                picking.customer_note = (
                    picking.sale_id.picking_customer_note
                    or picking.partner_id.picking_customer_note
                )
