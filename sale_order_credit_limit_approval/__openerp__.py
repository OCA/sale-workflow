# -*- coding: utf-8 -*-
##############################################################################
#
#    Mandate module for openERP
#    Copyright (C) 2015 Anubía, soluciones en la nube,SL (http://www.anubia.es)
#    @author: Juan Formoso <jfv@anubia.es>,
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
    'name': 'Sale Order Credit Limit Approval',
    'summary': 'Need of validation by responsible when sale order exceeds '
               'credit limit',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Juan Formoso <jfv@anubia.es>',
    'website': 'http://www.anubia.es',
    'category': 'Sale',
    'depends': [
        'sale',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/sale_workflow.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
