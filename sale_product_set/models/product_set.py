# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models
from odoo.osv import expression


class ProductSet(models.Model):
    _inherit = "product.set"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = expression.AND(
            [args, ["|", ("name", operator, name), ("id", operator, name)]]
        )
        records = self.search(domain, limit=limit)
        return [(rec.id, rec.display_name or "") for rec in records]
