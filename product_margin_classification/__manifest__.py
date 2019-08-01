# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product Margin Classification',
    'version': '10.0.1.0.0',
    'category': 'Account',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'description': """
This module is designed to extend Sale Price computation in Odoo.

This module add a new model 'Margin Classifications' linked to Product
Templates.

A margin classification has a 'Profit Margin' field and extra fields to manage
computation method, like in Pricelist Item model
(Markup Rate, Rounding and Surcharge fields)

If product has a margin classification defined and the theoretical price is
not the same as the sale price, an extra field 'Theoretical Price' is
displayed, based on the Margin Classification and a button is available to
change sale price.
""",
    'depends': [
        'account',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'data/decimal_precision.xml',
        'views/action.xml',
        'views/menu.xml',
        'views/view_product_template.xml',
        'views/view_product_margin_classification.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/product_margin_classification.xml',
        'demo/product_template.xml',
    ],
    'installable': True,
}
