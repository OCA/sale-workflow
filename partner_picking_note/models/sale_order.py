# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picking_note = fields.Html(compute="_compute_picking_note")
    picking_customer_note = fields.Text(compute="_compute_picking_note")

    @api.depends("partner_id")
    def _compute_picking_note(self):
        for order in self:
            order.picking_note = order.partner_id.picking_note
            order.picking_customer_note = order.partner_id.picking_customer_note
