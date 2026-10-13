from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    so_force_split = fields.Boolean(string="Force Split Sales Orders")
    so_split_strategy_id = fields.Many2one(
        comodel_name="sale.order.split.strategy",
        help="The strategy that will be used to split the sales order",
    )
