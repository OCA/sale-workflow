# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def copy(self, default=None):
        sale_copy = super().copy(default)
        # we unlink pack lines that should not be copied
        pack_copied_lines = sale_copy.order_line.filtered(
            lambda l: l.pack_parent_line_id.order_id == self)
        pack_copied_lines.unlink()
        return sale_copy

    @api.onchange('order_line')
    def check_pack_line_unlink(self):
        """At least on embeded tree editable view odoo returns a recordset on
        _origin.order_line only when lines are unlinked and this is exactly
        what we need
        """
        if self._origin.order_line.filtered(
            lambda x: x.pack_parent_line_id and
                not x.pack_parent_line_id.product_id.pack_modifiable):
            raise UserError(_(
                'You can not delete this line because is part of a pack in'
                ' this sale order. In order to delete this line you need to'
                ' delete the pack itself'))
