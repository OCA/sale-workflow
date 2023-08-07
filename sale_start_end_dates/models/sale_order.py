# Copyright 2014-2021 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date


class SaleOrder(models.Model):
    _inherit = "sale.order"

    default_start_date = fields.Date(
        compute="_compute_default_start_date", readonly=False, store=True
    )
    default_end_date = fields.Date(
        compute="_compute_default_end_date", readonly=False, store=True
    )

    @api.constrains("default_start_date", "default_end_date")
    def _check_default_start_end_dates(self):
        for order in self:
            if (
                order.default_start_date
                and order.default_end_date
                and order.default_start_date > order.default_end_date
            ):
                raise ValidationError(
                    _(
                        "Default Start Date (%(start_date)s) should be before or be the "
                        "same as Default End Date (%(end_date)s) for sale order '%(name)s'."
                    )
                    % {
                        "start_date": format_date(self.env, order.default_start_date),
                        "end_date": format_date(self.env, order.default_end_date),
                        "name": order.display_name,
                    }
                )

    @api.depends("default_end_date")
    def _compute_default_start_date(self):
        for order in self:
            if (
                order.default_start_date
                and order.default_end_date
                and order.default_start_date > order.default_end_date
            ):
                order.default_start_date = order.default_end_date

    @api.depends("default_start_date")
    def _compute_default_end_date(self):
        for order in self:
            if (
                order.default_start_date
                and order.default_end_date
                and order.default_start_date > order.default_end_date
            ):
                order.default_end_date = order.default_start_date


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    start_date = fields.Date(
        compute="_compute_start_date",
        store=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )
    end_date = fields.Date(
        compute="_compute_end_date",
        store=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )
    number_of_days = fields.Integer(
        compute="_compute_number_of_days",
        inverse="_inverse_number_of_days",
        readonly=False,
        store=True,
        string="Number of Days",
    )
    must_have_dates = fields.Boolean(related="product_id.must_have_dates")

    @api.depends("start_date", "end_date")
    def _compute_number_of_days(self):
        for line in self:
            days = False
            if line.start_date and line.end_date:
                days = (line.end_date - line.start_date).days + 1
            line.number_of_days = days

    @api.onchange("number_of_days")
    def _inverse_number_of_days(self):
        res = {"warning": {}}
        for line in self:
            if line.number_of_days < 0:
                res["warning"]["title"] = _("Wrong number of days")
                res["warning"]["message"] = _(
                    "On sale order line with product '%(product_name)s', the "
                    "number of days is negative (%(number_of_days)s) ; this is not "
                    "allowed. The number of days has been forced to 1."
                ) % {
                    "product_name": line.product_id.display_name,
                    "number_of_days": line.number_of_days,
                }
                line.number_of_days = 1
            if line.start_date:
                line.end_date = line.start_date + relativedelta(
                    days=line.number_of_days - 1
                )
            elif line.end_date:
                line.start_date = line.end_date - relativedelta(
                    days=line.number_of_days - 1
                )
        return res

    @api.constrains("product_id", "start_date", "end_date")
    def _check_start_end_dates(self):
        for line in self:
            if line.product_id.must_have_dates:
                if not line.end_date:
                    raise ValidationError(
                        _("Missing End Date for sale order line with " "Product '%s'.")
                        % (line.product_id.display_name)
                    )
                if not line.start_date:
                    raise ValidationError(
                        _(
                            "Missing Start Date for sale order line with "
                            "Product '%s'."
                        )
                        % (line.product_id.display_name)
                    )
                if line.start_date > line.end_date:
                    raise ValidationError(
                        _(
                            "Start Date (%(start_date)s) should be before or "
                            "be the same as End Date (%(end_date)s) for sale order line "
                            "with Product '%(product_name)s'."
                        )
                        % {
                            "start_date": format_date(self.env, line.start_date),
                            "end_date": format_date(self.env, line.end_date),
                            "product_name": line.product_id.display_name,
                        }
                    )

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        if not self.display_type and self.must_have_dates:
            res.update({"start_date": self.start_date, "end_date": self.end_date})
        return res

    @api.depends("end_date", "product_id")
    def _compute_start_date(self):
        for line in self:
            order = line.order_id
            if (
                not line.start_date
                and line.product_id.must_have_dates
                and order.default_start_date
            ):
                line.start_date = order.default_start_date
            elif line.start_date and not line.product_id.must_have_dates:
                line.start_date = False
            elif line.end_date and line.start_date and line.start_date > line.end_date:
                line.start_date = line.end_date

    @api.depends("start_date", "product_id")
    def _compute_end_date(self):
        for line in self:
            order = line.order_id
            if (
                not line.end_date
                and line.product_id.must_have_dates
                and order.default_end_date
            ):
                line.end_date = order.default_end_date
            elif line.end_date and not line.product_id.must_have_dates:
                line.end_date = False
            elif line.end_date and line.start_date and line.start_date > line.end_date:
                line.end_date = line.start_date
