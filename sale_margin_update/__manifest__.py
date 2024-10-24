###############################################################################
#
#    Sidoo Soluciones S.L.
#    Copyright (C) 2023-Today SDi Sidoo Soluciones S.L. <www.sidoo.es>
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
    "name": "Sale Margin Update",
    "summary": "Recalculate expected unit price from margin.",
    "author": "Oscar Soto, Sidoo Soluciones S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "version": "16.0.1.0.0",
    "depends": [
        "sale",
        "sales_team",
        "sale_margin",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "wizard/recalculate_price_margin.xml",
    ],
}
