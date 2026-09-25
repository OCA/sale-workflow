# Copyright 2026 Tecnativa - Carlos Roca
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Catalog Supplierinfo",
    "summary": "Add a supplier origin to the sale product catalog and pass the "
    "vendor to the order line",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_product_catalog_extended",
        "sale_purchase_force_vendor",
        "sale_line_vendor_comment",
        "product_supplierinfo_comment",
        # See product_pricelist.py's _get_applicable_rules() docstring for
        # why this is a real dependency despite the integration itself being
        # a soft, defensive one.
        "product_pricelist_supplierinfo",
    ],
    "data": [
        "views/sale_order_line_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            (
                "after",
                "sale_product_catalog_extended/static/src/product_catalog/search_panel.esm.js",
                "sale_product_catalog_supplierinfo/static/src/**/*",
            ),
        ],
    },
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["carlosdauden", "CarlosRoca13"],
}
