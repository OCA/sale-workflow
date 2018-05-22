##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def copy(self, default=None):
        sale_copy = super(SaleOrder, self).copy(default)
        # we unlink pack lines that should not be copied
        pack_copied_lines = sale_copy.order_line.filtered(
            lambda l: l.pack_parent_line_id.order_id == self)
        pack_copied_lines.unlink()
        return sale_copy
