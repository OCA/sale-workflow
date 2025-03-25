# Copyright 2024 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Partner Address Restrict",
    "summary": "Restrict addresses domain in the sales order form"
    " taking into account the partner selected",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base_partition",
        "sale",
    ],
    "data": [
        "views/sale_order_view.xml",
        "views/res_config_settings.xml",
        "views/res_partner_views.xml",
    ],
}
