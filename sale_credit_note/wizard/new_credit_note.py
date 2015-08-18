# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp


class sale_new_credit_note(orm.TransientModel):
    _name = "sale.new.credit.note"

    _columns = {
        'credit_amount': fields.float(
            'Credit note amount',
            digits_compute=dp.get_precision('Account')),
    }

    def _get_amount(self, cr, uid, context=None):
        res = 0
        if context is None:
            context = {}
        if context.get('active_id'):
            res = self.pool['account.invoice'].read(
                cr, uid, context['active_id'], context=context)['amount_total']
        return res

    _defaults = {
        'credit_amount': _get_amount,
        }

    def new_credit_note(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('active_id'):
            wizard = self.browse(cr, uid, ids[0], context=context)
            self.pool['account.invoice'].write(
                cr, uid, context['active_id'],
                {'credit_note_amount': wizard.credit_amount},
                context=context)
        return {'type': 'ir.actions.act_window_close'}
