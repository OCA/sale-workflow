# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Partner Shipping Default Partner Invoice",
    "summary": "Set invoice address based on shipping address for sales orders",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/res_partner_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
