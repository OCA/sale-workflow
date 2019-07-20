import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-partner_prospect',
        'odoo12-addon-portal_sale_personal_data_only',
        'odoo12-addon-sale_automatic_workflow',
        'odoo12-addon-sale_cancel_reason',
        'odoo12-addon-sale_commercial_partner',
        'odoo12-addon-sale_discount_display_amount',
        'odoo12-addon-sale_double_validation',
        'odoo12-addon-sale_exception',
        'odoo12-addon-sale_force_invoiced',
        'odoo12-addon-sale_last_price_info',
        'odoo12-addon-sale_merge_draft_invoice',
        'odoo12-addon-sale_milestone_profile_invoicing',
        'odoo12-addon-sale_order_action_invoice_create_hook',
        'odoo12-addon-sale_order_archive',
        'odoo12-addon-sale_order_general_discount',
        'odoo12-addon-sale_order_invoicing_finished_task',
        'odoo12-addon-sale_order_line_input',
        'odoo12-addon-sale_order_line_price_history',
        'odoo12-addon-sale_order_line_sequence',
        'odoo12-addon-sale_order_price_recalculation',
        'odoo12-addon-sale_order_revision',
        'odoo12-addon-sale_order_type',
        'odoo12-addon-sale_partner_incoterm',
        'odoo12-addon-sale_product_set',
        'odoo12-addon-sale_stock_picking_blocking',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
