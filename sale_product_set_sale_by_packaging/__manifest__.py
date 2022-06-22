# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sale Product Set Sale by packaging",
    "summary": """
    Glue module between `sale_by_packaging` and `sale_product_set_packaging_qty`.
    """,
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": ["sale_by_packaging", "sale_product_set_packaging_qty"],
    "data": [
        "data/ir_cron.xml",
        "views/product_set_line.xml",
        "views/product_template.xml",
    ],
}
