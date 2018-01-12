# -*- coding: utf-8 -*-
# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Sale Quotation Numeration',
    'summary': "Different sequence for sale quotations",
    'version': '10.0.1.0.0',
    'category': 'Sales Management',
    'website': 'https://odoo-community.org/',
    'author': 'Elico Corp,'
              'Agile Business Group,'
              'Odoo Community Association (OCA)'
              'Qubiq',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['sale'],
    'data': [
        'data/data.xml',
    ],
    'demo': [],
    'test': [],
}
