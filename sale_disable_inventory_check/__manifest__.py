# Copyright 2017 Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Disable Inventory Check",
    "summary": "Disable warning 'Not enough inventory' when there isn't enough"
               " product stock",
    "version": "11.0.2.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Nguyen Tan Phuc (komit-consulting.com), "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock", ],
    "data": [
        # Data
        'data/product_check_stock_data.xml',
        # Views
        'views/product_category_views.xml',
        'views/product_template_views.xml',
    ],
}
