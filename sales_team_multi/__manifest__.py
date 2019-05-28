{
    'name': "Multiple sales teams",

    'summary': """
        it allows to add an user to multiple teams or sales channels.""",

    'description': """
        it allows to add an user to multiple teams or sales channels.
    """,

    'author': "marco.martinez@Berrysoft, felipe.garcia@Berrysoft",
    'website': "http://www.berrysoft.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sales_team'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}