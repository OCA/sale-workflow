{
    "name": "Website Sale Payment",
    "version": "15.0.1.0.0",
    "category": "Website",
    "author": "ERP Harbor Consulting Services,"
    "Nitrokey GmbH,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": """
    Website Sale Payment is a part of sale-workflow and if the SO created has the payment method
    that has the boolean "Hold Picking until payment" enabled then stock picking will
    remain on "Hold" state until the payment is done.

    This functionality works the same If the Sale Order is created from website and
    Payment Method selected has the boolean "Hold Picking until payment" enabled then
    the Stock picking will remain on "Hold" state until the payment is done.
     """,
    "license": "AGPL-3",
    "depends": [
        "website_sale",
    ],
    "installable": True,
}
