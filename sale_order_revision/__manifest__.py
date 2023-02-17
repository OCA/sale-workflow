# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Dreambits Technologies Pvt. Ltd. (<http://dreambits.in>)
# Copyright 2020 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale order revisions",
    "summary": "Keep track of revised quotations",
    "version": "15.0.1.0.0",
    "category": "Sale Management",
    "author": "Agile Business Group,"
    "Dreambits,"
    "Camptocamp,"
    "Akretion,"
    "Serpent Consulting Services Pvt. Ltd.,"
    "Ecosoft,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["base_revision", "sale_management"],
    "data": ["view/sale_order.xml"],
    "installable": True,
    "post_init_hook": "populate_unrevisioned_name",
}
