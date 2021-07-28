# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product rating verified",
    "summary": """Verify if a user has previously bought a product""",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "sale",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "depends": ["rating", "account", "product"],
    "data": ["views/rating_view.xml"],
    "installable": True,
}
