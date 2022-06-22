# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    can_be_sold = fields.Boolean(
        string="Can be sold", compute="_compute_can_be_sold", readonly=False, store=True
    )

    force_sale_qty = fields.Boolean(
        string="Force sale quantity",
        help="Determine if during the creation of a sale order line, the "
        "quantity should be forced with a multiple of the packaging.\n"
        "Example:\n"
        "You sell a product by packaging of 5 products.\n"
        "When the user will put 3 as quantity, the system can force the "
        "quantity to the superior unit (5 for this example).",
    )

    @api.depends("packaging_type_id")
    def _compute_can_be_sold(self):
        for record in self:
            record.can_be_sold = record.packaging_type_id.can_be_sold
