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
from openerp import models, api, fields


class PaymentMethod(models.Model):
    _name = "payment.method"
    _description = "Payment Method"

    @api.model
    @api.returns('res.company')
    def _default_company_id(self):
        company_model = self.env['res.company']
        return company_model.browse(
            company_model._company_default_get('payment.method'))

    name = fields.Char(required=True,
                       help="The name of the method on the backend")
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        help="If a journal is selected, when a payment is recorded "
             "on a backend, payment entries will be created in this "
             "journal.",
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Payment Term',
        help="Default payment term of a sale order using this method.",
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=_default_company_id,
    )
