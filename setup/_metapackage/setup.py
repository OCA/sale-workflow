import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-sale-workflow",
    description="Meta package for oca-sale-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-sale_advance_payment',
        'odoo14-addon-sale_automatic_workflow',
        'odoo14-addon-sale_commercial_partner',
        'odoo14-addon-sale_commitment_date_mandatory',
        'odoo14-addon-sale_discount_display_amount',
        'odoo14-addon-sale_exception',
        'odoo14-addon-sale_force_invoiced',
        'odoo14-addon-sale_invoice_blocking',
        'odoo14-addon-sale_isolated_quotation',
        'odoo14-addon-sale_last_price_info',
        'odoo14-addon-sale_mrp_bom',
        'odoo14-addon-sale_order_archive',
        'odoo14-addon-sale_order_line_date',
        'odoo14-addon-sale_order_line_description',
        'odoo14-addon-sale_order_line_menu',
        'odoo14-addon-sale_order_line_note',
        'odoo14-addon-sale_order_lot_generator',
        'odoo14-addon-sale_order_lot_selection',
        'odoo14-addon-sale_order_note_template',
        'odoo14-addon-sale_order_qty_change_no_recompute',
        'odoo14-addon-sale_order_revision',
        'odoo14-addon-sale_partner_incoterm',
        'odoo14-addon-sale_pricelist_from_commitment_date',
        'odoo14-addon-sale_product_category_menu',
        'odoo14-addon-sale_product_multi_add',
        'odoo14-addon-sale_product_seasonality',
        'odoo14-addon-sale_product_set',
        'odoo14-addon-sale_product_set_packaging_qty',
        'odoo14-addon-sale_quotation_number',
        'odoo14-addon-sale_shipping_info_helper',
        'odoo14-addon-sale_stock_picking_blocking',
        'odoo14-addon-sale_tier_validation',
        'odoo14-addon-sale_validity',
        'odoo14-addon-sale_wishlist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
