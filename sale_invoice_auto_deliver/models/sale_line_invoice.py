# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, exceptions, models, _


class saleOrderLineMakeInvoice(models.TransientModel):
    _inherit = "sale.order.line.make.invoice"

    @api.model
    def _get_move_domain(self):
        return [('procurement_id.sale_line_id', 'in',
                 self.env.context.get('active_ids', [])),
                ('state', '=', 'assigned')]

    @api.multi
    def make_invoices(self):
        self.ensure_one()
        if self.env.context.get('auto_deliver'):
            # try to deliver all selected line
            # if all is delivered, make invoice
            # else raise exception
            move_not_done = True
            moves = self.env['stock.move'].search(self._get_move_domain())
            if moves:
                moves.action_done()
                move_not_done = moves.filtered(lambda x: x.state != 'done')
            if move_not_done:
                raise exceptions.Warning(
                    _("You cannot automatic deliver these order lines, "
                      "some products are not available"))

        return super(saleOrderLineMakeInvoice, self).make_invoices()
