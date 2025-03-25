# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Partner Address Restrict Dropshipping",
    "summary": "Hide parent contact name for dropshipping addresses.",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale_partner_address_restrict",
        "stock_dropshipping",
    ],
    "auto_install": True,
    "data": ["views/res_partner_views.xml"],
}
