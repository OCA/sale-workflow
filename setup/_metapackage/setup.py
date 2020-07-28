import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-sale_automatic_workflow',
        'odoo9-addon-sale_automatic_workflow_payment_mode',
        'odoo9-addon-sale_cancel_reason',
        'odoo9-addon-sale_delivery_block',
        'odoo9-addon-sale_delivery_block_proc_group_by_line',
        'odoo9-addon-sale_double_validation',
        'odoo9-addon-sale_exception',
        'odoo9-addon-sale_fixed_discount',
        'odoo9-addon-sale_force_invoiced',
        'odoo9-addon-sale_open_qty',
        'odoo9-addon-sale_order_digitized_signature',
        'odoo9-addon-sale_order_line_date',
        'odoo9-addon-sale_order_line_sequence',
        'odoo9-addon-sale_order_lot_selection',
        'odoo9-addon-sale_order_price_recalculation',
        'odoo9-addon-sale_order_product_recommendation',
        'odoo9-addon-sale_order_type',
        'odoo9-addon-sale_order_variant_mgmt',
        'odoo9-addon-sale_packaging_price',
        'odoo9-addon-sale_procurement_group_by_line',
        'odoo9-addon-sale_procurement_group_by_requested_date',
        'odoo9-addon-sale_product_set',
        'odoo9-addon-sale_rental',
        'odoo9-addon-sale_revert_done',
        'odoo9-addon-sale_sourced_by_line',
        'odoo9-addon-sale_start_end_dates',
        'odoo9-addon-sale_validity',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
