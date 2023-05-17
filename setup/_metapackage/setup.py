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
        'odoo-addon-product_supplierinfo_for_customer_sale>=16.0dev,<16.1dev',
        'odoo-addon-sale_automatic_workflow>=16.0dev,<16.1dev',
        'odoo-addon-sale_automatic_workflow_job>=16.0dev,<16.1dev',
        'odoo-addon-sale_automatic_workflow_payment_mode>=16.0dev,<16.1dev',
        'odoo-addon-sale_cancel_reason>=16.0dev,<16.1dev',
        'odoo-addon-sale_commercial_partner>=16.0dev,<16.1dev',
        'odoo-addon-sale_company_currency>=16.0dev,<16.1dev',
        'odoo-addon-sale_exception>=16.0dev,<16.1dev',
        'odoo-addon-sale_invoice_policy>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_archive>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_general_discount>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_line_menu>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_line_price_history>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_lot_generator>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_lot_selection>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_product_availability_inline>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_qty_change_no_recompute>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_revision>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_type>=16.0dev,<16.1dev',
        'odoo-addon-sale_partner_incoterm>=16.0dev,<16.1dev',
        'odoo-addon-sale_partner_selectable_option>=16.0dev,<16.1dev',
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
