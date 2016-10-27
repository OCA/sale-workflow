# -*- coding: utf-8 -*-
# © 2016 KMEE(http://www.kmee.com.br)
#   @author Hendrix Costa <hendrix.costa@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Order Invoice Link',
    'version': '9.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Add link from invoice to sale orders',
    'author': 'KMEE, Odoo Community Association (OCA)',
    'website': 'http://www.kmee.com.br',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml'
    ],
    'installable': True,
}
