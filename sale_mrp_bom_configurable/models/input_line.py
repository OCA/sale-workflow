from odoo import fields, models


class InputLine(models.Model):
    _inherit = "input.line"

    order_line_id = fields.Many2one(comodel_name="sale.order.line", ondelete="cascade")
