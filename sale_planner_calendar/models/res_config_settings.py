# Copyright 2020 Sergio Teruel - Tecnativa
# Copyright 2021 Tecnativa - Carlos Dauden
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    susbscriptions_backward_days = fields.Integer(
        related="company_id.susbscriptions_backward_days",
        readonly=False,
    )
    sale_planner_forward_months = fields.Integer(
        related="company_id.sale_planner_forward_months",
        readonly=False,
    )
    sale_planner_mail_to_attendees = fields.Boolean(
        related="company_id.sale_planner_mail_to_attendees",
        readonly=False,
    )
    sale_planner_order_cut_hour = fields.Float(
        related="company_id.sale_planner_order_cut_hour",
        readonly=False,
    )
    sale_planner_calendar_max_duration = fields.Float(
        string="Calendar event max duration",
        config_parameter="sale_planner_calendar.max_duration",
    )


class ResCompany(models.Model):
    _inherit = "res.company"

    susbscriptions_backward_days = fields.Integer(
        default=180,
    )
    sale_planner_forward_months = fields.Integer(
        default=12,
    )
    sale_planner_mail_to_attendees = fields.Boolean(
        string="Send invitation to attendees", default=True
    )
    sale_planner_order_cut_hour = fields.Float()
