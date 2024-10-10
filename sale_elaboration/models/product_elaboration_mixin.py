# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductElaborationMixin(models.AbstractModel):
    _name = "product.elaboration.mixin"
    _description = "Product Elaboration Mixin"

    elaboration_ids = fields.Many2many(
        comodel_name="product.elaboration",
        string="Elaborations",
    )
    elaboration_note = fields.Char(
        store=True,
    )
    is_elaboration = fields.Boolean(
        store=True,
        compute="_compute_is_elaboration",
        readonly=False,
    )

    @api.depends("product_id")
    def _compute_is_elaboration(self):
        """We use computed instead of a related field because related fields are not
        initialized with their value on one2many which related field is the
        inverse_name, so with this we get immediately the value on NewIds.
        """
        for line in self:
            line.is_elaboration = line.product_id.is_elaboration
