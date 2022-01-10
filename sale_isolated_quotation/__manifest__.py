# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Isolated Quotation",
    "version": "14.0.2.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_management", "sale_quotation_number"],
    "license": "AGPL-3",
    "images": [],
    "data": ["views/sale_views.xml"],
    "installable": True,
    "auto_install": False,
    "uninstall_hook": "uninstall_hook",
    "post_init_hook": "post_init_hook",
    "maintainers": ["bealdav", "kittiu"],
}
