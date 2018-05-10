# © 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2018 Roel Adriaans <roel@road-support.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Sake order Fiscal Position Update',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Changing the fiscal position of an sale order will auto-update '
               'order lines',
    'author': "Julius Network Solutions,"
              "Akretion,"
              "Road-Support,"
              "Odoo Community Association (OCA)",
    'depends': [
        'account',
        'sale',
    ],
    'installable': True,
}
