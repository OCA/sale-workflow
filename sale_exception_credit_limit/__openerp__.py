# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
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
{
    'name': 'Sale Exception Credit Limit',
    'version': '8.0.0.1.0',
    'description': """
Sale Exception Credit Limit
===========================
NOTE: this module replace partner_credit_limit that is going to be depreceated
on v9.
It adds a new group "can modify credit limit", only users with this group are
allowed to change credit limit on partners.

It also adds an exception to check that you can not aproove sale orders that
would exceed credit limit. It checks:
        * The credit the Partner has to paid
        * The amount of Sale Orders aproved but not yet invoiced
        * The invoices that are in draft state
        * The amount of the Sale Order to be aproved
and compares it with the credit limit of the partner. If the credit limit is
less it does not allow to approve the Sale Order
""",
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'sale_exceptions',
        ],
    'data': [
        'security/security.xml',
        'data/data.xml',
        'partner_view.xml',
        ],
    'demo': [
        'partner_demo.xml'
        ],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
