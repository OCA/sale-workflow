# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, exceptions, fields, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        selection_add=[
            ('all_auto',
             _('Invoice the whole sales order + Automatic Deliver'))])

    @api.model
    def _get_pickings(self, sale_ids):
        res = self.env['stock.picking']
        for so in self.env['sale.order'].browse(sale_ids):
            res += so.picking_ids
        return res

    @api.multi
    def create_invoices(self):
        self.ensure_one()
        if self.advance_payment_method == 'all_auto':
            # try to finalize sale pickings
            # if finalize is ok, set advance_payment_method to all
            # else raise exception
            sale_ids = self.env.context.get('active_ids', [])
            pickings = self._get_pickings(sale_ids).filtered(
                lambda x: x.state != 'done')
            picking_not_done = True
            if pickings:
                to_assign = pickings.filtered(lambda x: x.state != 'assigned')
                if to_assign:
                    to_assign.action_assign()
                if all([pick.state == 'assigned' for pick in pickings]):
                    for pick in pickings:
                        wiz = self.env['stock.immediate.transfer'].create(
                            {'pick_id': pick.id})
                        wiz.process()
                    picking_not_done = pickings.filtered(
                        lambda x: x.state != 'done')
                else:
                    picking_not_done = True
            if picking_not_done:
                raise exceptions.Warning(
                    _("You cannot automatic deliver this order, "
                      "some products are not available"))
            else:
                self.advance_payment_method = 'all'
        return super(SaleAdvancePaymentInv, self).create_invoices()
