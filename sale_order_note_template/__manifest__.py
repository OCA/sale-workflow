# © 2020 Pierre Verkest <pierreverkest84@gmail.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Orders Terms and conditions Templates",
    "summary": "Add sale orders terms and conditions template that can be "
    "used to quickly fullfill sale order terms and conditions",
    "category": "Sales/Sales",
    "version": "14.0.1.0.0",
    "author": "Pierre Verkest,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale_management",
    ],
    "data": [
        "views/sale_terms_template.xml",
        "views/sale_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
