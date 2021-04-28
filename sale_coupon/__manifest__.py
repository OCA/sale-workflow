
{
    'name': "Sale Coupon",
    'summary': "Use discount coupons in sales orders",
    'category': 'Sales',
    'version': '12.0.1.0.0',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_coupon_apply_code_views.xml',
        'wizard/sale_coupon_generate_views.xml',
        'views/sale_order_views.xml',
        'views/sale_coupon_views.xml',
        'views/sale_coupon_program_views.xml',
        'views/res_config_settings_views.xml',
        'report/sale_coupon_report.xml',
        'report/sale_coupon_report_templates.xml',
        'data/sale_coupon_email_data.xml',
    ],
    'demo': [
        'data/sale_coupon_demo.xml',
    ],
}
