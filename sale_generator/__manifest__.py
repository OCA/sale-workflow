#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author Abdessamad HILALI <abdessamad.hilali@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Generator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "sale",
    "version": "12.0.1.0.1",
    "license": "AGPL-3",
    "depends": ["sale_stock", "sale_management"],
    "data": [
        "data/data.xml",
        "views/generator_view.xml",
        "views/partner_view.xml",
        "views/sale_order_view.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
    ],
    "installable": True,
    "maintainers": ["sebastienbeau", "kevinkhao"],
}
