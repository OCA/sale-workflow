# Copyright 2012 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Product Special Types",
    "version": "11.0.1.0.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sales",
    "description":
    """
Add a special type selection on products.
Let create products as :
 - Global Discount
 - Delivery Costs
 - Advance

It add fields on the sale order and the invoice with the totals of each
product types.
These fields can be used on reports to display the amounts for
discounts / advances / fees separately.

""",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ['product'],
    "data": 'views/product_view.xml',
    'installable': False
}
