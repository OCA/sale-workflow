# Copyright 2024 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_default_invoice_policy = fields.Selection(
        [
            ("product", "Products Invoice Policy"),
            ("order", "Ordered quantities"),
            ("delivery", "Delivered quantities"),
        ],
        default="product",
        required=True,
        help="This will be the default invoice policy for sale orders.",
    )
