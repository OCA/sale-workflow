# -*- coding: utf-8 -*-
##############################################################################
#
#   sale_quick_payment for OpenERP
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#   Copyright 2013 Camptocamp SA (Guewen Baconnier)
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
##############################################################################

from openerp.osv import fields, orm


class payment_method(orm.Model):
    _name = "payment.method"
    _description = "Payment Method"

    _columns = {
        'name': fields.char('Name',
                            help="The name of the method on the backend",
                            required=True),
        'journal_id': fields.many2one(
            'account.journal',
            'Journal',
            help="If a journal a selected, when a payment is recorded "
                 "on a backend, payment entries will be created in this "
                 "journal. "),
        'payment_term_id': fields.many2one(
            'account.payment.term',
            'Payment Term',
             help="Default payment term of a sale order using this method."),
        'company_id': fields.many2one(
            'res.company',
            'Company',
        ),
    }

    def _default_company_id(self, cr, uid, context):
        company_model = self.pool.get('res.company')
        return company_model._company_default_get(cr, uid, 'payment.method',
                                                  context=context)

    _defaults = {
         'company_id': _default_company_id,
    }
