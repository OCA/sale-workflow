# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle, Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
#
{
    'name': "Sale Quotation Sourcing",

    'summary': "manual sourcing of sale quotations",
    'description': """
    This module implements manual sourcing of sale order lines from purchase
    order lines.

    Instead of having the confirmation of a SO generate procurements which in
    turn may generate a PO, we invert the process: in order to generate a quote
    for a customer, we ask quotes to different suppliers.

    Once the sale quotation is accepted by the customer and the user confirms
    it, a wizard is presented to choose which PO to use to source the SO lines.

    The process should mimic closely the way that Odoo handles a MTO, buy
    order. The only difference is that the PO is chosen manually and not
    automatically generated. The end result should be the same.

    To show that, two test cases are provided that show the standard process
    and the manually sourced one.

    The drop shipping case is handled as well, with a warning to check if the
    destination locations of the procurement and the sourced PO are consistent.
    In addition to that, when the user sources a sale line with a purchase
    line, the system tries to choose automatically an appropriate route (MTO or
    drophipping).

    This on_change method is the only place where the module stock_dropshipping
    is used, otherwise it contains little more than preconfigured Routes,
    Rules, and Picking Types. All other code and the tests do not use it.  That
    dependency can be easily removed later if it is needed to manually
    configure dropshipping and MTO routes.

    Note: the package nose is required to run the tests. It is not noted in the
    external dependencies since it is not required in production.

    """,

    'author': "Camptocamp",
    'website': "http://www.camptocamp.com",

    'category': 'Sales',
    'version': '0.3',

    'depends': ['sale_stock',
                'purchase',
                'stock_dropshipping',
                'sale_exceptions'],
    'data': ['views/sale_order_sourcing.xml',
             'views/sale_order.xml',
             'security/group.xml',
             'data/exceptions.xml',
             ],
    'test': [
        'test/setup_user.yml',
        'test/setup_product.yml',
        'test/setup_dropshipping.xml',
        'test/test_standard_mto_sourcing.yml',
        'test/test_standard_dropshipping.yml',
        'test/test_manual_mto_sourcing.yml',
        'test/test_manual_sourcing_dropshipping.yml',
    ],
}
