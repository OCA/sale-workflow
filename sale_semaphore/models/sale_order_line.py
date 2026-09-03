# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOderLine(models.Model):
    _inherit = "sale.order.line"

    semaphore_max_price_success = fields.Float(compute="_compute_semaphore_max_prices")
    semaphore_max_price_warning = fields.Float(compute="_compute_semaphore_max_prices")
    semaphore_max_price_danger = fields.Float(compute="_compute_semaphore_max_prices")
    semaphore_active = fields.Boolean(compute="_compute_semaphore", store=True)
    semaphore = fields.Selection(
        [
            ("success", "🟢"),
            ("warning", "🟡"),
            ("danger", "🔴"),
        ],
        compute="_compute_semaphore",
        store=True,
    )
    price_below_semaphore = fields.Boolean(compute="_compute_price_below_semaphore")

    @api.depends(
        "product_id", "price_reduce_taxinc", "price_reduce_taxexcl", "product_uom_id"
    )
    def _compute_semaphore(self):
        dp = self.env["decimal.precision"].precision_get("Product Price")
        self.semaphore_active = False
        for record in self:
            if not record.product_id or not record.product_uom_id:
                continue
            semaphore_data = record.product_id._get_semaphore_data()
            if not semaphore_data:
                continue
            record.semaphore_active = True
            price_reduce = record._get_semaphore_price_reduce()
            price_reduce = record.product_uom_id._compute_price(
                price_reduce, record.product_id.uom_id
            )
            if (
                float_compare(
                    record.product_id.lst_price
                    * ((100 - semaphore_data["success"]) / 100),
                    price_reduce,
                    precision_digits=dp,
                )
                <= 0
            ):
                record.semaphore = "success"
            elif (
                float_compare(
                    record.product_id.lst_price
                    * ((100 - semaphore_data["warning"]) / 100),
                    price_reduce,
                    precision_digits=dp,
                )
                <= 0
            ):
                record.semaphore = "warning"
            else:
                record.semaphore = "danger"

    @api.depends("product_id", "product_uom_id")
    def _compute_semaphore_max_prices(self):
        self.semaphore_max_price_success = self.semaphore_max_price_warning = (
            self.semaphore_max_price_danger
        ) = 0
        for record in self:
            if not record.product_id or not record.product_uom_id:
                continue
            semaphore_data = record.product_id._get_semaphore_data()
            if not semaphore_data:
                continue
            lst_price = record.product_id.uom_id._compute_price(
                record.product_id.lst_price, record.product_uom_id
            )
            record.semaphore_max_price_success = lst_price * (
                (100 - semaphore_data["success"]) / 100
            )
            record.semaphore_max_price_warning = lst_price * (
                (100 - semaphore_data["warning"]) / 100
            )
            record.semaphore_max_price_danger = lst_price * (
                (100 - semaphore_data["danger"]) / 100
            )

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals["semaphore"] = self.semaphore
        return vals

    def _get_semaphore_price_reduce(self):
        """Net unit price used to evaluate the semaphore, on the company's tax
        inclusion basis."""
        self.ensure_one()
        return (
            self.price_reduce_taxinc
            if self.company_id.account_price_include == "tax_included"
            else self.price_reduce_taxexcl
        )

    def _get_semaphore_pricelist_price(self):
        """Pricelist price for this line expressed on the same basis as
        :meth:`_get_semaphore_price_reduce` so both values are comparable.

        We must align three things, otherwise a line priced exactly at the
        pricelist looks like it is below it:

        - Unit of measure: ``_get_product_price`` returns the price in the
          product uom unless the line uom is passed.
        - Tax inclusion: ``price_reduce_taxinc`` includes taxes while the
          pricelist price is tax excluded, so taxes are applied when the
          company prices tax included.
        - Rounding: ``price_reduce_*`` is derived from monetary amounts rounded
          to the currency, while the pricelist price keeps the ``Product Price``
          precision (e.g. ``14.3202``). Rounding to the currency avoids the
          residual difference that would falsely trigger the semaphore block.
        """
        self.ensure_one()
        price = self.order_id.pricelist_id._get_product_price(
            self.product_id, self.product_uom_qty, uom=self.product_uom_id
        )
        if self.company_id.account_price_include == "tax_included":
            price = self.tax_ids.compute_all(
                price,
                currency=self.currency_id,
                quantity=1.0,
                product=self.product_id,
                partner=self.order_id.partner_id,
            )["total_included"]
        return self.currency_id.round(price)

    def _is_price_below_pricelist(self):
        """Return whether the line net price is actually lower than the price
        the pricelist would set (i.e. the salesperson lowered it)."""
        self.ensure_one()
        dp = self.env["decimal.precision"].precision_get("Product Price")
        return (
            float_compare(
                self._get_semaphore_price_reduce(),
                self._get_semaphore_pricelist_price(),
                precision_digits=dp,
            )
            < 0
        )

    @api.depends("semaphore_active", "price_reduce_taxinc", "price_reduce_taxexcl")
    def _compute_price_below_semaphore(self):
        dp = self.env["decimal.precision"].precision_get("Product Price")
        self.price_below_semaphore = False
        for record in self.filtered(lambda line: line.semaphore_active):
            record.price_below_semaphore = (
                float_compare(
                    record.semaphore_max_price_danger,
                    record._get_semaphore_price_reduce(),
                    precision_digits=dp,
                )
                > 0
            )

    def write(self, vals):
        res = super().write(vals)
        if ("price_unit" in vals or "discount" in vals) and not self.env.user.has_group(
            "sales_team.group_sale_manager"
        ):
            lines_below_semaphore = self.filtered(
                lambda line: line.price_below_semaphore
                and line.state in ["sale", "done"]
            )
            if lines_below_semaphore.filtered(
                lambda line: line._is_price_below_pricelist()
            ):
                raise UserError(
                    self.env._(
                        "There's a line with price below semaphore's accepted.\n\n"
                        "Please set the prices in a way that they are accepted "
                        "by the semaphore, or contact the purchasing "
                        "administrators."
                    )
                )
        return res
