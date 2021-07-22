# Copyright 2021 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderTag(models.Model):
    _name = "sale.order.tag"
    _order = "name"
    _description = "Sale Order Tag"

    name = fields.Char(required=True)
    description = fields.Text(string="Description")
    color = fields.Integer(string="Color Index")
    team_ids = fields.Many2many("crm.team", string="Sales Teams")
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one("res.company", string="Company")
    sequence = fields.Integer(
        default=lambda self: self.env["ir.sequence"].next_by_code("sale.order.tag")
        or 0,
        required=True,
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Tag name already exists!")]
