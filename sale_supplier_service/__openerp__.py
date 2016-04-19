# coding: utf-8
# @ 2016 Florian da Costa @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Sale Supplier Service',
 'version': '8.0.1.0.0',
 'author': 'Akretion,Odoo Community Association (OCA)',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Sales Management',
 'summary': """
    Allow to automatically create purchase order when a service product
    is sold.
 """,
 'depends': [
     'purchase',
     'sale',
 ],
 'data': [
     'view/product_view.xml'
 ],
 'installable': True,
 'application': False,
 }
