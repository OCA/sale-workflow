# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from .partner import POINT_OPERATIONS


class PointHistory(models.Model):
    _name = "credit.point.history"
    _rec_name = "partner_id"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
    )
    operation = fields.Selection(
        selection=POINT_OPERATIONS,
        required=True,
    )
    amount = fields.Monetary(
        currency_field="credit_point_currency_id",
        readonly=True,
        default=0,
        required=True,
    )
    credit_point_currency_id = fields.Many2one(
        related="partner_id.credit_point_currency_id",
        readonly=True,
    )
    create_date = fields.Datetime()
    comment = fields.Char()
