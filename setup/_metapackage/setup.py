import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-sale_advance_payment>=15.0dev,<15.1dev',
        'odoo-addon-sale_automatic_workflow>=15.0dev,<15.1dev',
        'odoo-addon-sale_blanket_order>=15.0dev,<15.1dev',
        'odoo-addon-sale_commercial_partner>=15.0dev,<15.1dev',
        'odoo-addon-sale_delivery_state>=15.0dev,<15.1dev',
        'odoo-addon-sale_discount_display_amount>=15.0dev,<15.1dev',
        'odoo-addon-sale_force_invoiced>=15.0dev,<15.1dev',
        'odoo-addon-sale_invoice_plan>=15.0dev,<15.1dev',
        'odoo-addon-sale_invoice_policy>=15.0dev,<15.1dev',
        'odoo-addon-sale_order_invoice_amount>=15.0dev,<15.1dev',
        'odoo-addon-sale_order_line_date>=15.0dev,<15.1dev',
        'odoo-addon-sale_order_qty_change_no_recompute>=15.0dev,<15.1dev',
        'odoo-addon-sale_order_type>=15.0dev,<15.1dev',
        'odoo-addon-sale_procurement_group_by_line>=15.0dev,<15.1dev',
        'odoo-addon-sale_product_category_menu>=15.0dev,<15.1dev',
        'odoo-addon-sale_product_multi_add>=15.0dev,<15.1dev',
        'odoo-addon-sale_rental>=15.0dev,<15.1dev',
        'odoo-addon-sale_sourced_by_line>=15.0dev,<15.1dev',
        'odoo-addon-sale_start_end_dates>=15.0dev,<15.1dev',
        'odoo-addon-sale_tier_validation>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
