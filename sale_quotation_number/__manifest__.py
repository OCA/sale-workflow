{
    "name": "Sale Quotation Numeration",
    "summary": "Different sequence for sale quotations",
    "version": "16.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        # data
        "data/ir_sequence_data.xml",
        # views
        "views/sales_config.xml",
    ],
    "application": False,
    "installable": True,
}
