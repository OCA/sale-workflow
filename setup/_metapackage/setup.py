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
        'odoo13-addon-sale_discount_display_amount',
        'odoo13-addon-sale_last_price_info',
        'odoo13-addon-sale_order_archive',
        'odoo13-addon-sale_product_multi_add',
        'odoo13-addon-sale_product_set',
        'odoo13-addon-sale_wishlist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
