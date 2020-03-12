# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# Copyright 2020 Daniel Reis - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_note = fields.Text(
        string="Picking Note",
    )

    def _update_pickings_note(self, picking_note=None):
        pickings = self.mapped(
            'picking_ids').filtered(lambda s: s.state != 'done')
        for picking in pickings:
            sale_note = picking_note or picking.sale_id.picking_note
            picking.note = sale_note

    def _action_confirm(self):
        super()._action_confirm()
        self._update_pickings_note()

    def write(self, values):
        if 'picking_note' in values and self.mapped('picking_ids'):
            can_update_picking_notes = self.env.user.has_group(
                'sale_stock_picking_note.group_sale_picking_note_edit')
            if not can_update_picking_notes:
                raise UserError(_(
                    'Cannot update the Picking notes '
                    'after Pickings are created.'
                ))
            self._update_pickings_note(values['picking_note'])
        return super().write(values)
