import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-partner_contact_sale_info_propagation>=16.0dev,<16.1dev',
        'odoo-addon-partner_sale_pivot>=16.0dev,<16.1dev',
        'odoo-addon-sale_automatic_workflow>=16.0dev,<16.1dev',
        'odoo-addon-sale_automatic_workflow_payment_mode>=16.0dev,<16.1dev',
        'odoo-addon-sale_commercial_partner>=16.0dev,<16.1dev',
        'odoo-addon-sale_exception>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_archive>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_line_menu>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_lot_generator>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_lot_selection>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_type>=16.0dev,<16.1dev',
        'odoo-addon-sale_stock_picking_blocking>=16.0dev,<16.1dev',
        'odoo-addon-sale_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-sale_triple_discount>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
