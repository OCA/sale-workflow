# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Jordi Ballester Alomar <jordi.ballester@eficent.com>
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
    "name": "Sale Dropshipping Location",
    "version": "1.0",
    "author": "Eficent",
    "website": "",
    "category": "Generic Modules/Sale",
    "depends": ["sale_dropshipping"],
    "description": """
    Introduces the possibility to receive drop shipment stock into
    a virtual location within the company, where the reception
    move is automatically chained to the default customer location.

    As a consequence of this change, products that are handled
    with real-time inventory valuation can properly record the
    accounting entries:
        * Stock Move supplier->drop shipment locations:
            - Debit: Stock valuation
            - Credit: Stock Input (this is a Liability account)
        * Stock Move drop shipment -> drop shipment locations:
            - Debit: Stock Output (this is an expense account)
            - Credit: Stock Valuation


    """,
    "init_xml": [],
    "update_xml": [
        "data/stock_data.xml",
        "view/stock_warehouse_view.xml",
    ],
    'demo_xml': [

    ],
    'test':[
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}
