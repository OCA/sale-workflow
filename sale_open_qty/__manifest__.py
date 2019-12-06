# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (https://openindustry.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Open Qty",
    "summary": "Allows to identify the sale orders that have quantities "
               "pending to deliver.",
    "version": "11.0.1.0.0",
    "author": "Openindustry, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sale",
    "depends": [
        "sale_stock",
        "sale_order_line_input",
    ],
    "data": [
        "views/sale_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
