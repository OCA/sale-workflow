# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    @author Lorenzo Battistini <lorenzo.battistini@agilebg.com>
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

{
    'name': "Sale order revisions",
    'version': '8.0.0.1.0',
    'category': 'Sale Management',
    'description': """
Revisions for sale orders (and requests for quotation)
==========================================================

On canceled orders, you can click on 'new revision' and the 'old revisions'
tab of the just created request for quotation will contain all the old
(canceled orders) revisions.
So that you can track every change you made to your requests for quotation and
sale orders.
""",
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['sale'],
    "data": [
        'sale_view.xml',
        ],
    "demo": [],
    "test": [
        'test/sale_order.yml',
        ],
    "active": False,
    "installable": True
}
