# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014-2015 Serv. Tecnol. Av. (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza Romero <pedro.baeza@serviciosbaeza.com>
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
    "name": "Back to draft on sales orders",
    "version": "8.0.1.0.0",
    "category": "Sales Management",
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.serviciosbaeza.com",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
    ],
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
