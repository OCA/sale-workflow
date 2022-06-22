# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Mail Autosubscribe",
    "summary": "Automatically subscribe partners to their company's sale orders",
    "version": "15.0.1.0.0",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "license": "AGPL-3",
    "category": "Sale",
    "depends": ["mail_autosubscribe", "sale"],
    "website": "https://github.com/OCA/sale-workflow",
    "data": ["data/mail_autosubscribe.xml"],
    "auto_install": True,
}
