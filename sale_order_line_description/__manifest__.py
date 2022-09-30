# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2013-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
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
#
{
    "name": "Sale order line description",
    "version": "10.0.1.0.0",
    "category": "Sales Management",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "installable": True,
    "website": "https://github.com/OCA/sale-workflow"
               "10.0/sale_order_line_description",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "security/sale_security.xml",
        "views/res_config_view.xml",
    ]
}
