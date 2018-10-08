import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-partner_prospect',
        'odoo11-addon-sale_automatic_workflow',
        'odoo11-addon-sale_automatic_workflow_payment_mode',
        'odoo11-addon-sale_commercial_partner',
        'odoo11-addon-sale_exception',
        'odoo11-addon-sale_force_invoiced',
        'odoo11-addon-sale_invoice_group_method',
        'odoo11-addon-sale_last_price_info',
        'odoo11-addon-sale_merge_draft_invoice',
        'odoo11-addon-sale_order_action_invoice_create_hook',
        'odoo11-addon-sale_order_archive',
        'odoo11-addon-sale_order_general_discount',
        'odoo11-addon-sale_order_invoicing_finished_task',
        'odoo11-addon-sale_order_line_date',
        'odoo11-addon-sale_order_line_input',
        'odoo11-addon-sale_order_price_recalculation',
        'odoo11-addon-sale_order_product_recommendation',
        'odoo11-addon-sale_order_revision',
        'odoo11-addon-sale_order_type',
        'odoo11-addon-sale_product_set',
        'odoo11-addon-sale_product_set_variant',
        'odoo11-addon-sale_quotation_number',
        'odoo11-addon-sale_start_end_dates',
        'odoo11-addon-sale_stock_picking_note',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
