# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Elaboration(models.Model):
    _name = "product.elaboration"
    _description = "Product elaborations"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(string="Short Code")
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        ondelete="restrict",
        domain=[("type", "=", "service"), ("is_elaboration", "=", True)],
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the product "
        "elaborations without removing it.",
    )

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Name must be unique!"),
        ("code_uniq", "unique(code)", "Code must be unique!"),
    ]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Give preference to codes on name search, appending
        the rest of the results after.
        """
        if not args:
            args = []
        recs = self.search([("code", operator, name)] + args, limit=limit)
        res = recs.name_get()
        if limit:
            limit_rest = limit - len(recs)
        else:  # pragma: no cover
            # limit can be 0 or None representing infinite
            limit_rest = limit
        if limit_rest or not limit:
            args += [("id", "not in", recs.ids)]
            res += super().name_search(
                name, args=args, operator=operator, limit=limit_rest
            )
        return res
