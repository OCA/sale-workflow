# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_note = fields.Text(
        string="Picking Note",
    )

    @api.onchange(
        'partner_id',
    )
    def onchange_partner_picking_note(self):
        partner = self.partner_id
        if partner:
            partner_picking_note = partner.default_picking_note
            self.picking_note = partner_picking_note


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        sale_note = self.sale_line_id.order_id.picking_note
        if sale_note:
            vals['note'] = sale_note
        return vals
