# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Sébastien Beau
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#    Copyright 2013 Camptocamp SA (Guewen Baconnier)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import logging
from openerp import api, models, fields, exceptions, _
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('amount_total', 'payment_ids.credit', 'payment_ids.debit')
    def _compute_amount(self):
        paid_amount = sum(line.credit - line.debit
                          for line in self.payment_ids)
        self.amount_paid = paid_amount
        self.residual = self.amount_total - paid_amount

    payment_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Payments Entries',
        domain=[('account_id.type', '=', 'receivable')],
        copy=False,
    )
    payment_method_id = fields.Many2one(
        comodel_name='payment.method',
        string='Payment Method',
        ondelete='restrict',
    )
    residual = fields.Float(
        compute='_compute_amount',
        digits_compute=dp.get_precision('Account'),
        string='Balance',
        store=False,
    )
    amount_paid = fields.Float(
        compute='_compute_amount',
        digits_compute=dp.get_precision('Account'),
        string='Amount Paid',
        store=False,
    )

    @api.multi
    def action_cancel(self):
        for sale in self:
            if sale.payment_ids:
                raise exceptions.Warning(_('Cannot cancel this sales order '
                                           'because automatic payment entries '
                                           'are linked with it.'))
        return super(SaleOrder, self).action_cancel()

    @api.multi
    def automatic_payment(self, amount=None):
        """ Create the payment entries to pay a sale order, respecting
        the payment terms.
        If no amount is defined, it will pay the residual amount of the sale
        order.
        """
        self.ensure_one()
        method = self.payment_method_id
        if not method:
            raise exceptions.Warning(
                _("An automatic payment can not be created for the sale "
                  "order %s because it has no payment method.") % self.name
            )

        if not method.journal_id:
            raise exceptions.Warning(
                _("An automatic payment should be created for the sale order"
                  " %s but the payment method '%s' has no journal defined.") %
                (self.name, method.name)
            )

        journal = method.journal_id
        date = self.date_order[:10]
        if amount is None:
            amount = self.residual
        if self.payment_term:
            amounts = self.payment_term.compute(amount, date_ref=date)[0]
        else:
            amounts = [(date, amount)]

        # reversed is cosmetic, compute returns terms in the 'wrong' order
        for date, amount in reversed(amounts):
            self._add_payment(journal, amount, date)
        return True

    @api.multi
    def add_payment(self, journal_id, amount, date=None, description=None):
        """ Generate payment move lines of a certain amount linked
        with the sale order.
        """
        self.ensure_one()
        journal_model = self.env['account.journal']
        if date is None:
            date = self.date_order
        journal = journal_model.browse(journal_id)
        self._add_payment(journal, amount, date, description)
        return True

    @api.multi
    def _add_payment(self, journal, amount, date, description=None):
        """ Generate move lines entries to pay the sale order. """
        move_model = self.env['account.move']
        period_model = self.env['account.period']
        period = period_model.find(dt=date)
        move_name = description or self._get_payment_move_name(journal, period)
        move_vals = self._prepare_payment_move(move_name, journal,
                                               period, date)
        move_lines = self._prepare_payment_move_lines(move_name, journal,
                                                      period, amount, date)

        move_vals['line_id'] = [(0, 0, line) for line in move_lines]
        move_model.create(move_vals)

    @api.model
    def _get_payment_move_name(self, journal, period):
        sequence = journal.sequence_id
        if not sequence:
            raise exceptions.Warning(_('Please define a sequence on the '
                                       'journal %s.') % journal.name)
        if not sequence.active:
            raise exceptions.Warning(_('Please activate the sequence of the '
                                       'journal %s.') % journal.name)

        sequence = sequence.with_context(fiscalyear_id=period.fiscalyear_id.id)
        # next_by_id not compatible with new api
        sequence_model = self.pool['ir.sequence']
        name = sequence_model.next_by_id(self.env.cr, self.env.uid,
                                         sequence.id,
                                         context=self.env.context)
        return name

    @api.multi
    def _prepare_payment_move(self, move_name, journal, period, date):
        return {'name': move_name,
                'journal_id': journal.id,
                'date': date,
                'ref': self.name,
                'period_id': period.id,
                }

    @api.multi
    def _prepare_payment_move_line(self, move_name, journal, period,
                                   amount, date):
        # to remove in v9
        _logger.warning('Deprecated: _prepare_payment_move_line has been '
                        'deprecated in favor of _prepare_payment_move_lines')
        return self._prepare_payment_move_lines(move_name, journal, period,
                                                amount, date)

    @api.multi
    def _prepare_payment_move_lines(self, move_name, journal, period,
                                    amount, date):
        partner = self.partner_invoice_id.commercial_partner_id
        company = journal.company_id

        currency = self.env['res.currency'].browse()
        # if the lines are not in a different currency,
        # the amount_currency stays at 0.0
        amount_currency = 0.0
        if journal.currency and journal.currency != company.currency_id:
            # when the journal have a currency, we have to convert
            # the amount to the currency of the company and set
            # the journal's currency on the lines
            currency = journal.currency
            company_amount = currency.compute(amount, company.currency_id)
            amount_currency, amount = amount, company_amount

        # payment line (bank / cash)
        debit_line = {
            'name': move_name,
            'debit': amount,
            'credit': 0.0,
            'account_id': journal.default_credit_account_id.id,
            'journal_id': journal.id,
            'period_id': period.id,
            'partner_id': partner.id,
            'date': date,
            'amount_currency': amount_currency,
            'currency_id': currency.id,
        }

        # payment line (receivable)
        credit_line = {
            'name': move_name,
            'debit': 0.0,
            'credit': amount,
            'account_id': partner.property_account_receivable.id,
            'journal_id': journal.id,
            'period_id': period.id,
            'partner_id': partner.id,
            'date': date,
            'amount_currency': -amount_currency,
            'currency_id': currency.id,
            'sale_ids': [(4, self.id)],
        }
        return debit_line, credit_line

    @api.onchange('payment_method_id')
    def onchange_payment_method_id_set_payment_term(self):
        if not self.payment_method_id:
            return
        method = self.payment_method_id
        if method.payment_term_id:
            self.payment_term = method.payment_term_id.id

    @api.multi
    def action_view_payments(self):
        """ Return an action to display the payment linked
        with the sale order """
        self.ensure_one()

        moves = self.mapped('payment_ids.move_id')

        xmlid = ('account', 'action_move_journal_line')
        action = self.env['ir.actions.act_window'].for_xml_id(*xmlid)
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        else:
            ref = self.env.ref('account.view_move_form')
            action['views'] = [(ref.id, 'form')]
            action['res_id'] = moves.id if moves else False
        return action
