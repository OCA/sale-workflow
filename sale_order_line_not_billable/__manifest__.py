{
    "name": "Sale Order Line Not Billable",
    "summary": """
        Set product as not billable and ensure its filtered when invoicing the sale order.
    """,
    "author": "Mint System GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": ["views/product_template.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["images/screen.png"],
}
