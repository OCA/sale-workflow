# Copyright 2021 Pingo Tecnologia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Author: Eder Brito <britoederr@gmail.com>

{
    'name': 'Sale Crm Set Won',
    'summary': """
        Set Won CRM Opportunity When Done a Sale Order""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Pingo Tecnologia, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
	    'sale_crm',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
    'demo': [
    ],
}
