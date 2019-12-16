# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Sale Product Returnable',
    'summary': "Get returnable products from your customers",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'author': 'Serpent Consulting Services, '
              'Open Source Integrators, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'development_status': 'Production/Stable',
    'depends': ['sale_stock'],
    'maintainers': ['max3903'],
    'data': [
        'views/product_template_view.xml',
    ],
    'application': False,
}
