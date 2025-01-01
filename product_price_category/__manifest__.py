# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Price Category",
    "summary": "Add Price Category field on product and allow to apply "
    "a pricelist on this field.",
    "version": "16.0.1.0.0",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Product",
    "depends": ["sale_stock"],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "security/ir.model.access.csv",
        "views/product_pricelist.xml",
        "views/product_template.xml",
    ],
    "maintainers": ["sbejaoui"],
    "installable": True,
}
