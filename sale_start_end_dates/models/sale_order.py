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

    default_start_date = fields.Date()
    default_end_date = fields.Date()

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
                        "Default Start Date ({start_date}) should be before or be the "
                        "same as Default End Date ({end_date}) for sale order '{name}'."
                    ).format(
                        start_date=format_date(self.env, order.default_start_date),
                        end_date=format_date(self.env, order.default_end_date),
                        name=order.display_name,
                    )
                )

    @api.onchange("default_start_date")
    def default_start_date_change(self):
        if (
            self.default_start_date
            and self.default_end_date
            and self.default_start_date > self.default_end_date
        ):
            self.default_end_date = self.default_start_date

    @api.onchange("default_end_date")
    def default_end_date_change(self):
        if (
            self.default_start_date
            and self.default_end_date
            and self.default_start_date > self.default_end_date
        ):
            self.default_start_date = self.default_end_date


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    start_date = fields.Date(
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )
    end_date = fields.Date(
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )
    number_of_days = fields.Integer(
        compute="_compute_number_of_days",
        inverse="_inverse_number_of_days",
        readonly=False,
        store=True,
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
                    "On sale order line with product '{product_name}', the "
                    "number of days is negative ({number_of_days}) ; this is not "
                    "allowed. The number of days has been forced to 1."
                ).format(
                    product_name=line.product_id.display_name,
                    number_of_days=line.number_of_days,
                )
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
                            "Start Date ({start_date}) should be before or "
                            "be the same as End Date ({end_date}) for sale order line "
                            "with Product '{product_name}'."
                        ).format(
                            start_date=format_date(self.env, line.start_date),
                            end_date=format_date(self.env, line.end_date),
                            product_name=line.product_id.display_name,
                        )
                    )

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        if not self.display_type and self.must_have_dates:
            res.update({"start_date": self.start_date, "end_date": self.end_date})
        return res

    @api.onchange("end_date")
    def end_date_change(self):
        if self.end_date:
            if self.start_date and self.start_date > self.end_date:
                self.start_date = self.end_date

    @api.onchange("start_date")
    def start_date_change(self):
        if self.start_date:
            if self.end_date and self.start_date > self.end_date:
                self.end_date = self.start_date

    @api.onchange("product_id")
    def start_end_dates_product_id_change(self):
        if self.product_id.must_have_dates:
            if self.order_id.default_start_date:
                self.start_date = self.order_id.default_start_date
            else:
                self.start_date = False
            if self.order_id.default_end_date:
                self.end_date = self.order_id.default_end_date
            else:
                self.end_date = False
        else:
            self.start_date = False
            self.end_date = False
