# -*- encoding: utf-8 -*-
#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author Abdessamad HILALI <abdessamad.hilali@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Sale Generator",
    'author': "Akretion",
    'website': "http://www.Akretion.com",
    'category': 'sale',
    'version': '10.0.1.O.O',
    'depends': ['sale_stock'],
    'data': [
        'data/data.xml',
        'views/generator_view.xml',
        'views/sale_view.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        ],
    'demo': [],
}


