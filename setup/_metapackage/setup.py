import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-sale_automatic_workflow',
        'odoo11-addon-sale_automatic_workflow_payment_mode',
        'odoo11-addon-sale_commercial_partner',
        'odoo11-addon-sale_exception',
        'odoo11-addon-sale_invoice_group_method',
        'odoo11-addon-sale_merge_draft_invoice',
        'odoo11-addon-sale_order_action_invoice_create_hook',
        'odoo11-addon-sale_order_invoicing_finished_task',
        'odoo11-addon-sale_order_line_date',
        'odoo11-addon-sale_order_line_input',
        'odoo11-addon-sale_order_price_recalculation',
        'odoo11-addon-sale_order_type',
        'odoo11-addon-sale_product_set',
        'odoo11-addon-sale_product_set_variant',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
