# Copyright 2022 Ashish Hirpara <ashish.hirapara1995@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Default Sale UOM",
    "summary": """ Set default Unit of Measure value of a product in sales order lines.""",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "author": "Ashish Hirpara, Ooops, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "contributors": ["Ashish-Hirpara"],
    "maintainers": ["ashishhirapara"],
    "depends": ["sale_management"],
    "license": "AGPL-3",
    "data": [
        "views/product_template_view.xml",
    ],
    "installable": True,
}
