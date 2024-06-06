# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale MRP Bom Configurable",
    "summary": "Skip components lines in bom according to conditions",
    "version": "16.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp_bom_configurable", "sale", "sale_mrp_bom"],
    "maintainer": [
        "franzpoize",
    ],
    "data": [
        "views/sale_order.xml",
        "views/sale_order_line.xml",
        "views/sale_price_config.xml",
        "wizard/wizard_copy_input_line_data.xml",
        "wizard/matrix_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_mrp_bom_configurable/static/src/view_controller.esm.js",
        ],
    },
    "installable": True,
}
