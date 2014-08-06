# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Comments for sale documents (order, picking and invoice)",
    "version": "1.0",
    "depends": [
        "base",
        "sale_stock",
        "sale",
        "stock_account",
        "stock",
        "account",
    ],
    "author": "OdooMRP team",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "summary": "",
    "description": """
With this module you can add specific comments to a customer, for sale order,
delivery order and invoices. Part of the info will be passed from one to other.
Those data will be automatically added to each item.
    """,
    "data": [
        "views/partner_view.xml",
        "views/sale_view.xml",
        "views/stock_view.xml",
        "views/account_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
