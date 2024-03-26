{
    "name": "Sale Product Advance Payment",
    "version": "14.0.1.0.0",
    "author": "Ilyas, Ooops, Odoo Community Association (OCA)",
    "category": "Sales",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/pdp.xml",
        "views/sale.xml",
        "wizard/sale_make_invoice_advance_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
