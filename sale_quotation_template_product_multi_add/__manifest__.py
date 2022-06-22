{
    "name": "Sale Quotation Template Product Multi Add",
    "summary": """
        Feature to add multiple products to quotation template """,
    "author": "Ilyas, Ooops404, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sale Management",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/sale_template_add_products_view.xml",
        "views/sale_view.xml",
    ],
}
