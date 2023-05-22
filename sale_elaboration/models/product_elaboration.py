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
        default=True,
        help="If unchecked, it will allow you to hide the product "
        "elaborations without removing it.",
    )
    route_ids = fields.Many2many(
        comodel_name="stock.location.route",
        string="Routes",
        domain=[("sale_selectable", "=", True)],
        ondelete="restrict",
        check_company=True,
    )
    profile_ids = fields.Many2many(
        comodel_name="product.elaboration.profile",
        relation="product_elaboration_profile_rel",
        column1="elaboration_id",
        column2="profile_id",
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
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([("code", "=ilike", name)] + args, limit=limit)
        if not recs:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()
