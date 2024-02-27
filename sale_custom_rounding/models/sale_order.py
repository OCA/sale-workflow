# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tax_calculation_rounding_method = fields.Selection(
        [
            ("round_per_line", "Round per Line"),
            ("round_globally", "Round Globally"),
        ],
        compute="_compute_tax_calculation_rounding_method",
        store=True,
        readonly=False,
        help="How total tax amount is computed. If no value selected, "
        "the method defined in the company is used.",
    )

    @api.depends("partner_invoice_id")
    def _compute_tax_calculation_rounding_method(self):
        for record in self:
            tax_calculation_rounding_method = False
            if (
                record.partner_invoice_id
                and record.partner_invoice_id.tax_calculation_rounding_method
            ):
                tax_calculation_rounding_method = (
                    record.partner_invoice_id.tax_calculation_rounding_method
                )
            record.tax_calculation_rounding_method = tax_calculation_rounding_method

    @api.depends("tax_calculation_rounding_method")
    def _compute_tax_totals_json(self):
        ret = True
        if self.filtered(
            lambda a: a.tax_calculation_rounding_method == "round_per_line"
        ):
            ret = super(
                SaleOrder,
                self.filtered(
                    lambda a: a.tax_calculation_rounding_method == "round_per_line"
                ).with_context(round=True),
            )._compute_tax_totals_json()
        if self.filtered(
            lambda a: a.tax_calculation_rounding_method == "round_globally"
        ):
            ret = super(
                SaleOrder,
                self.filtered(
                    lambda a: a.tax_calculation_rounding_method == "round_globally"
                ).with_context(round=False),
            )._compute_tax_totals_json()
        if self.filtered(lambda a: not a.tax_calculation_rounding_method):
            ret = super(
                SaleOrder,
                self.filtered(lambda a: not a.tax_calculation_rounding_method),
            )._compute_tax_totals_json()
        return ret

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        # It is important to include or ''. Otherwise, the grouping process fails.
        vals["tax_calculation_rounding_method"] = (
            self.tax_calculation_rounding_method or ""
        )
        return vals

    def _get_invoice_grouping_keys(self):
        return super()._get_invoice_grouping_keys() + [
            "tax_calculation_rounding_method"
        ]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.tax_calculation_rounding_method")
    def _compute_amount(self):
        ret = True
        if self.filtered(
            lambda a: a.order_id.tax_calculation_rounding_method == "round_per_line"
        ):
            ret = super(
                SaleOrderLine,
                self.filtered(
                    lambda a: a.order_id.tax_calculation_rounding_method
                    == "round_per_line"
                ).with_context(round=True),
            )._compute_amount()
        if self.filtered(
            lambda a: a.order_id.tax_calculation_rounding_method == "round_globally"
        ):
            ret = super(
                SaleOrderLine,
                self.filtered(
                    lambda a: a.order_id.tax_calculation_rounding_method
                    == "round_globally"
                ).with_context(round=False),
            )._compute_amount()
        if self.filtered(lambda a: not a.order_id.tax_calculation_rounding_method):
            ret = super(
                SaleOrderLine,
                self.filtered(lambda a: not a.order_id.tax_calculation_rounding_method),
            )._compute_amount()
        return ret
