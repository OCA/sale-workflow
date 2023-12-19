# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_note = fields.Html(
        string="Picking Internal Note",
        compute="_compute_picking_notes",
        store=True,
        readonly=False,
    )
    picking_customer_note = fields.Text(
        string="Picking Customer Comments",
        compute="_compute_picking_notes",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_picking_notes(self):
        for order in self:
            if order.state not in {"sale", "done", "cancel"}:
                order.picking_note = (
                    order.partner_shipping_id.picking_note
                    or order.partner_id.picking_note
                )
                order.picking_customer_note = (
                    order.partner_shipping_id.picking_customer_note
                    or order.partner_id.picking_customer_note
                )
