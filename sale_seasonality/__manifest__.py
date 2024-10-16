# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Seasonality",
    "summary": """Sale Seasonality""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["product_simple_seasonality", "sale"],
    "data": [
        "views/seasonality.xml",
        "views/utm_campaign.xml",
        "views/product.xml",
        "security/campaign_seasonality.xml",
        "reports/sale_report.xml",
    ],
    "demo": [
        "demo/data.xml",
    ],
    "maintainers": ["bealdav", "kevinkhao"],
}
