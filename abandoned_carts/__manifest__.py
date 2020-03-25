{
    'name': "Abandoned Carts",
    'version': '12.0.1.0.0',
    'depends': ['website_sale','crm','account','project', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
        'views/removed_record_log_views.xml',
        'wizard/sale_order_view.xml',
        'wizard/customer_view.xml',
        
    ],
    'author': "Nitrokey GmbH, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': "https://github.com/OCA/abandoned_carts",
    
}
