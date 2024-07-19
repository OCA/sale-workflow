{
    'name': 'Sale Milestone Profile Invoicing',
    'summary': """Inform on delivered and invoiced work by sale order line.""",
    'version': '12.0.1.0.2',
    'license': 'AGPL-3',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'sale',
        'sale_timesheet',
    ],
    'data': [
        'views/sale_milestone_profile_invoicing.xml',
    ],
    'installable': True,
}
