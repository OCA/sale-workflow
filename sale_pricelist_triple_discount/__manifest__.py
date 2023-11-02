#  Copyright (c) 2015 credativ ltd (<http://www.credativ.co.uk>)
#  Copyright (c) 2020 Simone Rubino - Agile Business Group
#  Copyright 2023 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Pricelist Triple Discount",
    "version": "16.0.1.0.0",
    "category": "Sale",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow"
    "16.0/sale_pricelist_triple_discount",
    "license": "AGPL-3",
    "depends": [
        "sale_triple_discount",
    ],
    "data": [
        "view/product_pricelist_item_views.xml",
    ],
    "auto_install": False,
    "installable": True,
}
