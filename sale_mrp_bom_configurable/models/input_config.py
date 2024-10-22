from odoo import fields, models


class InputConfig(models.Model):
    _inherit = "input.config"

    order_id = fields.Many2one(comodel_name="sale.order", ondelete="cascade")
