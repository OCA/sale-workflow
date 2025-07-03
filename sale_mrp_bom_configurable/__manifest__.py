# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale MRP Bom Configurable",
    "summary": "Skip components lines in bom according to conditions",
    "version": "16.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "mrp_bom_configurable",
        "sale",
        "sale_management",
        "sale_mrp_bom",
        "sale_order_lot_selection",
    ],
    "maintainer": [
        "franzpoize",
    ],
    "data": [
        "views/sale_order.xml",
        "views/sale_order_line.xml",
        "views/sale_price_config.xml",
        "wizard/matrix_wizard.xml",
        "wizard/wizard_copy_input_line_data.xml",
        "wizard/wizard_sale_price_change.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_mrp_bom_configurable/static/src/xml/matrix_table.xml",
            "sale_mrp_bom_configurable/static/src/js/matrix_table.esm.js",
            "sale_mrp_bom_configurable/static/src/xml/sale_price_config_change_button.xml",
            "sale_mrp_bom_configurable/static/src/js/sale_price_config_change_button.esm.js",
            "sale_mrp_bom_configurable/static/src/css/matrix_table.scss",
            "sale_mrp_bom_configurable/static/src/css/sale_order_line_tree_view.scss",
        ],
    },
    "installable": True,
}
