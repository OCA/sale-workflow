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
    elaboration_note = fields.Char()
    is_elaboration = fields.Boolean(
        store=True,
        compute="_compute_is_elaboration",
        readonly=False,
    )

    @api.onchange("elaboration_ids")
    def onchange_elaboration_ids(self):
        """Use onchange method instead of compute because if any other data of any line
        force a recompute of all lines and the elaboration custom notes are reset.
        """
        for line in self:
            line.elaboration_note = ", ".join(line.elaboration_ids.mapped("name"))

    @api.depends("product_id")
    def _compute_is_elaboration(self):
        """We use computed instead of a related field because related fields are not
        initialized with their value on one2many which related field is the
        inverse_name, so with this we get immediately the value on NewIds.
        """
        for line in self:
            line.is_elaboration = line.product_id.is_elaboration
