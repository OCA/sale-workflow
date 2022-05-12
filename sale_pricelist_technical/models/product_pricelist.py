# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    is_technical = fields.Boolean(
        string="Is Technical",
        help="Check this box if you want to prevent user to use"
        " this pricelist on the orders, or in the customer form."
        " This is usefull for pricelist created only to compute"
        " other pricelists.",
    )
