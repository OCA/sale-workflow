from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    general_discount = fields.Selection(
        [
            ("discount1", "Discount 1"),
            ("discount2", "Discount 2"),
            ("discount3", "Discount 3"),
        ],
        required=False,
        config_parameter="sale_order_general_discount_triple.general_discount",
    )
    pricelist_discount = fields.Selection(
        [
            ("discount1", "Discount 1"),
            ("discount2", "Discount 2"),
            ("discount3", "Discount 3"),
        ],
        required=False,
        config_parameter="sale_order_general_discount_triple.pricelist_discount",
    )
