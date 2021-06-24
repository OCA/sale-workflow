# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    secondary_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Secondary Salesperson",
        track_visibility="onchange",
    )

    _sql_constraints = [
        (
            "secondary_user_id",
            "CHECK((secondary_user_id IS NULL) OR (secondary_user_id != user_id))",
            "The secondary salesperson must be different from the primary salesperson!",
        ),
    ]
