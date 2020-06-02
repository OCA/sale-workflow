import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-sale_automatic_workflow',
        'odoo13-addon-sale_automatic_workflow_payment',
        'odoo13-addon-sale_commercial_partner',
        'odoo13-addon-sale_discount_display_amount',
        'odoo13-addon-sale_elaboration',
        'odoo13-addon-sale_force_invoiced',
        'odoo13-addon-sale_last_price_info',
        'odoo13-addon-sale_order_archive',
        'odoo13-addon-sale_order_line_date',
        'odoo13-addon-sale_order_lot_selection',
        'odoo13-addon-sale_order_product_recommendation',
        'odoo13-addon-sale_order_product_recommendation_secondary_unit',
        'odoo13-addon-sale_order_secondary_unit',
        'odoo13-addon-sale_order_type',
        'odoo13-addon-sale_partner_incoterm',
        'odoo13-addon-sale_procurement_group_by_line',
        'odoo13-addon-sale_product_multi_add',
        'odoo13-addon-sale_product_set',
        'odoo13-addon-sale_shipping_info_helper',
        'odoo13-addon-sale_stock_delivery_address',
        'odoo13-addon-sale_stock_secondary_unit',
        'odoo13-addon-sale_tier_validation',
        'odoo13-addon-sale_wishlist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
