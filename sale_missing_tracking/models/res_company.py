# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_missing_max_delay_times = fields.Integer(
        string="Max delay times",
        help="Number of times that a salesperson can postpone the response "
        "to the follow-up",
        default=1,
    )
    sale_missing_days_from = fields.Integer(
        string="Days from",
        help="Number of days before to today to take into account the beginning "
        "of the period to obtain sold products",
        default=45,
    )
    sale_missing_days_to = fields.Integer(
        string="Days to",
        help="Number of days before to today to take into account the ending "
        "of the period to obtain sold products",
        default=15,
    )
    sale_missing_days_notification = fields.Integer(
        string="Days notification",
        help="Number of days from the first advice to create a notification",
        default=30,
    )
    sale_missing_months_consumption = fields.Integer(
        string="Months consumption",
        help="Number of months to compute product consumption",
        default=12,
    )
    sale_missing_minimal_consumption = fields.Monetary(
        string="Minimal consumption",
        help="Minimal consumption in months consumption",
        default=1000.0,
    )
