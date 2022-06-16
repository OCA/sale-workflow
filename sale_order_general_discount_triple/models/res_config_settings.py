from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    general_discount = fields.Selection(
        [
            ("discount", "Discount"),
            ("discount2", "Discount 2"),
            ("discount3", "Discount 3"),
        ],
        "General Discount",
        required=True,
        default="discount",
        config_parameter="sale_order_general_discount_triple.general_discount",
    )
