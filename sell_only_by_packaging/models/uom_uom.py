# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    force_sale_qty = fields.Boolean(
        string="Force sale quantity",
        help="Determine if during the creation of a sale order line sold in "
        "this unit, the quantity should be forced to a whole number of "
        "this unit.\n"
        "Example:\n"
        "You sell a product by packaging of 5 products.\n"
        "When the user will put 0.6 packaging as quantity, the system can "
        "force the quantity to the superior unit (1 packaging, so 5 "
        "products, for this example).",
    )
