from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    input_config_id = fields.Many2one(
        comodel_name="input.config",
    )
