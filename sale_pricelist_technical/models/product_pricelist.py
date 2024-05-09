# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    is_technical = fields.Boolean(
        help="Check this box if you want to prevent users from using"
        " this pricelist on orders or in customer forms."
        " This is useful for pricelists that are created only to compute"
        " other pricelists.",
    )
