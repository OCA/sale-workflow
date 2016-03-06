# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Partner Order Policy module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Sale Partner Order Policy',
    'version': '8.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': "Adds customer create invoice method on partner form",
    'description': """
This module adds a new field on the partner form in the *Accouting* tab:
*Customer Create Invoice*. The value of this field will be used when you
create a new Sale Order with this partner as customer.

Beware that this module depends not only on *sale*, but also on *stock*.
As there is only one create invoice method when the *stock* module is not
installed, you should not install this module if the *stock* module is not
installed.

This module has been written by Alexis de Lattre
<alexis.delattre@akretion.com>
    """,
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'depends': ['sale_stock'],
    'data': ['partner_view.xml'],
    'demo': ['partner_demo.xml'],
    'installable': True,
}
