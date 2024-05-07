# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pricelist Cache",
    "summary": """
        Provide a new model to cache price lists and update it,
        to make it easier to retrieve them.
    """,
    "version": "15.0.1.4.1",
    "category": "Hidden",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "partner_pricelist_search",
        "base_automation",
        "product",
        "sale",
        "queue_job",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "security/ir.model.access.csv",
        "data/base_automation.xml",
        "data/ir_cron.xml",
        "data/ir_filters_data.xml",
        "data/queue_job.xml",
        "views/res_partner.xml",
        "views/product_pricelist.xml",
        "views/product_pricelist_cache.xml",
        "wizards/pricelist_cache_wizard.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "installable": True,
    "post_init_hook": "set_default_partner_product_filter",
}
