from odoo import fields, models

class StockLot(models.Model):
    _name = "stock.lot"
    _inherit = "stock.lot"

    input_line_id = fields.Many2one(comodel_name="input.line")
