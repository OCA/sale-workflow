##############################################################################
#
#    OmniaSolutions, Open Source Management Solution
#    2010-2018 OmniaSolutions (<http://www.omniasolutions.eu>).
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
##############################################################################

{
    "name": "Sale Order Margin Percent",
    "summary": "Show Percent in sale order",
    "version": "10.0.1.0.0",
    "category": "Sales",
    "website": "http://www.pesol.es",
    "author": "PESOL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'sale',
        'sale_margin'
    ],
    "data": [
        'views/sale_order_margin_percent_view.xml',
    ]
}
