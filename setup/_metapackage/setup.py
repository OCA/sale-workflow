import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-sale_commercial_partner',
        'odoo14-addon-sale_last_price_info',
        'odoo14-addon-sale_order_archive',
        'odoo14-addon-sale_order_lot_selection',
        'odoo14-addon-sale_product_category_menu',
        'odoo14-addon-sale_product_multi_add',
        'odoo14-addon-sale_validity',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
