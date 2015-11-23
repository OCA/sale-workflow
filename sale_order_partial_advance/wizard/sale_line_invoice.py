# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp.tools.translate import _


class SaleOrderLineMakeInvoice(models.TransientModel):
    _inherit = 'sale.order.line.make.invoice'

    order_ids = fields.One2many(string='Sale Orders',
                                comodel_name='sale.order.make.invoice',
                                inverse_name='wizard_id')

    @api.model
    def default_get(self, fields_list):
        '''
            Extract all sale orders impacted in order to suggest to the user
            a table containing:
            - order reference
            - advance amount still available
            - advance amount he wants to use
            If all the lines of the sale order are selected the advance amount
            to use is automatically set to the amount available
        '''
        defaults = super(SaleOrderLineMakeInvoice,
                         self).default_get(fields_list)
        lines = self.env['sale.order.line'].browse(
            self.env.context.get('active_ids', []))
        orders = set([line.order_id for line in lines
                      if line.order_id.advance_amount_available > 0])
        if orders:
            order_ids = []
            for order in orders:
                all_lines = True
                res = [line.id for line in order.order_line
                       if line not in lines and not line.invoiced]
                if res:
                    all_lines = False
                to_use = order.advance_amount_available if all_lines else 0.0
                order_ids.append(
                    (0, 0, {'wizard_id': self.id,
                            'order_id': order.id,
                            'advance_amount_available':
                            order.advance_amount_available,
                            'advance_amount_to_use': to_use,
                            'all_lines': all_lines}))
            defaults['order_ids'] = order_ids
        return defaults

    @api.model
    def _prepare_invoice(self, order, lines):
        # retrieve the context from order recordset because the method caller
        # does not pass it
        wizard = order.env.context.get('instance')
        order_adv_data = wizard.order_ids.filtered(
            lambda x: x.order_id.id == order.id)
        if order_adv_data:
            advance_prod_id =\
                self.env['sale.advance.payment.inv']._get_advance_product()
            inv_l_obj = self.env['account.invoice.line']
            val = inv_l_obj.product_id_change(
                advance_prod_id, False, partner_id=order.partner_id.id,
                fposition_id=order.fiscal_position.id,
                company_id=order.company_id.id)
            inv_line_values = val['value']
            inv_line_values['product_id'] = advance_prod_id
            inv_line_values['name'] = _('Part of advance (%s %s) used'
                                        % (order.advance_amount,
                                           order.company_id.currency_id.symbol)
                                        )
            inv_line_values['price_unit'] =\
                -order_adv_data.advance_amount_to_use
            adv_line = inv_l_obj.create(inv_line_values)
            lines.append(adv_line.id)

        return super(SaleOrderLineMakeInvoice, self)._prepare_invoice(order,
                                                                      lines)

    @api.multi
    def make_invoices(self):
        self = self.with_context(instance=self)
        return super(SaleOrderLineMakeInvoice,
                     self).make_invoices()


class SaleOrderMakeInvoice(models.TransientModel):
    _name = 'sale.order.make.invoice'

    wizard_id = fields.Many2one(string='Wizard',
                                comodel_name='sale.order.line.make.invoice',
                                required=True)
    order_id = fields.Many2one(string='Sale Order',
                               comodel_name='sale.order',
                               required=True)
    advance_amount_available = fields.Float('Advance Available')
    advance_amount_to_use = fields.Float('Advance To Use',
                                         required=True,
                                         default=0.0)
    all_lines = fields.Boolean('All Sale Order Lines Selected')
