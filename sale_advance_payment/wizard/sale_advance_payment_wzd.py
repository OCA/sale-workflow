##############################################################################
#
#    Copyright (C) 2015 Comunitea Servicios Tecnológicos All Rights Reserved
#    $Omar Castiñeira Saaevdra <omar@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, exceptions, _


class AccountVoucherWizard(models.TransientModel):

    _name = "account.voucher.wizard"

    @api.multi
    @api.depends('journal_id')
    def _get_journal_currency(self):
        for wzd in self:
            wzd.journal_currency_id = wzd.journal_id.currency_id.id or \
                self.env.user.company_id.currency_id.id

    journal_id = fields.Many2one('account.journal', 'Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    journal_currency_id = fields.Many2one("res.currency", "Journal Currency",
                                          readonly=True,
                                          compute="_get_journal_currency")
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)
    amount_total = fields.Monetary('Amount total', readonly=True)
    amount_advance = fields.Monetary('Amount advanced', required=True)
    date = fields.Date("Date", required=True,
                       default=fields.Date.context_today)
    exchange_rate = fields.Float("Exchange rate", digits=(16, 6), default=1.0,
                                 readonly=True)
    currency_amount = fields.Monetary("Curr. amount", readonly=True,
                                      currency_field="journal_currency_id")
    payment_ref = fields.Char("Ref.")

    @api.constrains('amount_advance')
    def check_amount(self):
        if self.amount_advance <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be "
                                               "positive."))
        if self.env.context.get('active_id', False):
            order = self.env["sale.order"].\
                browse(self.env.context['active_id'])
            if self.amount_advance > order.amount_resisual:
                raise exceptions.ValidationError(_("Amount of advance is "
                                                   "greater than residual "
                                                   "amount on sale"))

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        sale_ids = self.env.context.get('active_ids', [])
        if not sale_ids:
            return res
        sale_id = sale_ids[0]

        sale = self.env['sale.order'].browse(sale_id)

        if 'amount_total' in fields:
            res.update({'amount_total': sale.amount_resisual,
                        'currency_id': sale.pricelist_id.currency_id.id})

        return res

    @api.onchange('journal_id', 'date', 'amount_advance')
    def onchange_date(self):
        sale_obj = self.env['sale.order']

        sale_ids = self.env.context.get('active_ids', [])
        if sale_ids:
            sale_id = sale_ids[0]
            sale = self.env['sale.order'].browse(sale_id)
            if self.currency_id:
                self.exchange_rate = 1.0 / \
                    (self.env["res.currency"].
                    _get_conversion_rate(sale.company_id.currency_id,self.currency_id,
                                        sale.company_id, self.date)
                    or 1.0)
            else:
                self.exchange_rate = 1.0
            self.currency_amount = self.amount_advance * (1.0 / self.exchange_rate)

    @api.multi
    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        self.ensure_one()
        payment_obj = self.env['account.payment']
        sale_obj = self.env['sale.order']

        sale_ids = self.env.context.get('active_ids', [])
        if sale_ids:
            sale_id = sale_ids[0]
            sale = sale_obj.browse(sale_id)

            partner_id = sale.partner_id.commercial_partner_id.id
            company = sale.company_id

            payment_res = {'payment_type': 'inbound',
                           'partner_id': partner_id,
                           'partner_type': 'customer',
                           'journal_id': self.journal_id.id,
                           'company_id': company.id,
                           'currency_id':
                           sale.pricelist_id.currency_id.id,
                           'payment_date': self.date,
                           'amount': self.amount_advance,
                           'sale_id': sale.id,
                           'name': _("Advance Payment") + " - " + sale.name,
                           'communication': self.payment_ref or sale.name,
                           'payment_reference': self.payment_ref or sale.name,
                           'payment_method_id': self.env.
                           ref('account.account_payment_method_manual_in').id
                           }
            payment = payment_obj.create(payment_res)
            payment.post()

        return {
            'type': 'ir.actions.act_window_close',
        }
