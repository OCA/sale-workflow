# Copyright 2021 Akretion France (http://www.akretion.com/)
# Copyright 2024 Akretion France (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SalePrimeship(models.Model):
    _name = "sale.primeship"
    _description = "Sale Prime Memberships"

    active = fields.Boolean(default=True)
    name = fields.Char(compute="_compute_name")

    start_date = fields.Date(required=True)
    # End date day is not included in primeship date range
    end_date = fields.Date(required=True)

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
        index=True,
    )
    order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
    )
    order_id = fields.Many2one(string="Sale Order", related="order_line_id.order_id")

    current = fields.Boolean(string="Currently Active", compute="_compute_current")

    _sql_constraints = [
        # Constraint for One2one impl of "sale.order.line".primeship_id
        (
            "unique_order_line",
            "UNIQUE(order_line_id)",
            "A sale order line can only have one primeship!",
        )
    ]

    @api.depends("start_date", "end_date")
    def _compute_name(self):
        for record in self:
            record.name = (
                f"{record.start_date} - {record.end_date} Primeship"
                if record
                else "New Primeship"
            )

    @api.depends("active", "start_date", "end_date")
    def _compute_current(self):
        for record in self:
            record.current = (
                record.active
                and record.start_date
                <= fields.Date.context_today(record)
                < record.end_date
            )

    @api.constrains("end_date")
    def _check_end_date(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError(_("The end date cannot be before start date"))

            if any(
                primeship.overlaps(record.start_date, record.end_date)
                for primeship in record.partner_id.primeship_ids
                if primeship.id != record.id
            ):
                raise ValidationError(_("Primeships cannot overlaps"))

    def overlaps(self, start, end):
        self.ensure_one()
        return self.start_date < end and self.end_date > start
