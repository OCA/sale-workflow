# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Dreambits Technologies Pvt. Ltd. (<http://dreambits.in>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale order revisions",
    "summary": "Keep track of revised quotations",
    "version": "12.0.1.0.0",
    "category": "Sale Management",
    "author": "Agile Business Group,"
              "Dreambits,"
              "Camptocamp,"
              "Akretion,"
              "Odoo Community Association (OCA), "
              "Serpent Consulting Services Pvt. Ltd.",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale_management",
    ],
    "data": [
        "view/sale_order.xml",
    ],
    "installable": True,
    "post_init_hook": "populate_unrevisioned_name",
}
