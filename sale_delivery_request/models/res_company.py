from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    delivery_request_expiration_days = fields.Integer(
        string="Delivery Request Expiration (days)",
        default=15,
        help="Number of calendar days after the response date before "
        "a confirmed delivery request expires.",
    )
