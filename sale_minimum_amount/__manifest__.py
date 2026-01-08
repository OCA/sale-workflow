{
    "name": "Sale Minimum Amount",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Minimum sale order amount per customer",
    "author": "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_order_approval_block",
    ],
    "data": [
        "data/sale_block_reason_data.xml",
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
