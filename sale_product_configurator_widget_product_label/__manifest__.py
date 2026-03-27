{
    "name": "Sale product configurator widget product label",
    "version": "17.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "web_widget_product_label_section_and_note",
        "sale_product_configurator",
    ],
    "data": ["views/sale_order_views.xml"],
    "assets": {
        "web.assets_backend": [
            "sale_product_configurator_widget_product_label/static/src/components/**/*",
        ],
    },
    "installable": True,
    "auto_install": True,
    "maintainers": ["carlos-lopez-tecnativa"],
    "license": "AGPL-3",
}
