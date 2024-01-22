# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Technical Pricelists for Sales",
    "summary": "Prevent some pricelists from being selected on order and"
    " customer forms",
    "version": "16.0.1.0.1",
    "category": "Product",
    "author": "GRAP,Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": ["views/view_product_pricelist.xml"],
    "demo": ["demo/product_pricelist.xml"],
    "installable": True,
}
