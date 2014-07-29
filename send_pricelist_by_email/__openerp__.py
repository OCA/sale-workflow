# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
###############################################################################

{
    'name': 'Send pricelist version by email',
    "version": "1.0",
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'depends': [
        'product',
        'report_webkit',
        'base_headers_webkit',
        'mail',
    ],
    'category': 'Sales Management',
    'description': """
Send pricelist version by email
===============================

This module allow to send a pricelist version by email.

It adds in the system :
* a new mail template
* a button "Send by email" in the pricelist version form view
* the abitlity to print the pricelist version.

So far the module does not drill down through pricelist items that are
based on another pricelist or based on purchase pricelists.

Contributors
------------
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
* Vincent Vinet (vincent.vinet@savoirfairelinux.com)
    """,
    'data': [
        'send_pricelist_by_email_report.xml',
        'send_pricelist_by_email_view.xml',
        'send_pricelist_by_email_data.xml',
    ],
    'active': False,
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
