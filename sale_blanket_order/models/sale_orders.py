# Copyright 2018 ACSONE SA/NV
# Copyright 2019 Eficent and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    blanket_order_id = fields.Many2one(
        "sale.blanket.order",
        string="Origin blanket order",
        related="order_line.blanket_order_line.order_id",
    )

    @api.model
    def _check_exchausted_blanket_order_line(self):
        return any(
            line.blanket_order_line.remaining_qty < 0.0 for line in self.order_line
        )

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order._check_exchausted_blanket_order_line():
                raise ValidationError(
                    _(
                        "Cannot confirm order %s as one of the lines refers "
                        "to a blanket order that has no remaining quantity."
                    )
                    % order.name
                )
        return res

    @api.constrains("partner_id")
    def check_partner_id(self):
        for line in self.order_line:
            if line.blanket_order_line:
                if line.blanket_order_line.partner_id != self.partner_id:
                    raise ValidationError(
                        _(
                            "The customer must be equal to the "
                            "blanket order lines customer"
                        )
                    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    blanket_order_line = fields.Many2one(
        "sale.blanket.order.line", string="Blanket Order line", copy=False
    )

    def _get_assigned_bo_line(self, bo_lines):
        # We get the blanket order line with enough quantity and closest
        # scheduled date
        assigned_bo_line = False
        date_planned = date.today()
        date_delta = timedelta(days=365)
        for line in bo_lines.filtered(lambda l: l.date_schedule):
            date_schedule = line.date_schedule
            if date_schedule and abs(date_schedule - date_planned) < date_delta:
                assigned_bo_line = line
                date_delta = abs(date_schedule - date_planned)
        if assigned_bo_line:
            return assigned_bo_line
        non_date_bo_lines = bo_lines.filtered(lambda l: not l.date_schedule)
        if non_date_bo_lines:
            return non_date_bo_lines[0]

    def _get_eligible_bo_lines_domain(self, base_qty):
        filters = [
            ("product_id", "=", self.product_id.id),
            ("remaining_qty", ">=", base_qty),
            ("currency_id", "=", self.order_id.currency_id.id),
            ("order_id.state", "=", "open"),
        ]
        if self.order_id.partner_id:
            filters.append(("partner_id", "=", self.order_id.partner_id.id))
        return filters

    def _get_eligible_bo_lines(self):
        base_qty = self.product_uom._compute_quantity(
            self.product_uom_qty, self.product_id.uom_id
        )
        filters = self._get_eligible_bo_lines_domain(base_qty)
        return self.env["sale.blanket.order.line"].search(filters)

    def get_assigned_bo_line(self):
        self.ensure_one()
        eligible_bo_lines = self._get_eligible_bo_lines()
        if eligible_bo_lines:
            if (
                not self.blanket_order_line
                or self.blanket_order_line not in eligible_bo_lines
            ):
                self.blanket_order_line = self._get_assigned_bo_line(eligible_bo_lines)
        else:
            self.blanket_order_line = False
        self.onchange_blanket_order_line()
        return {"domain": {"blanket_order_line": [("id", "in", eligible_bo_lines.ids)]}}

    @api.onchange("product_id", "order_partner_id")
    def onchange_product_id(self):
        # If product has changed remove the relation with blanket order line
        if self.product_id:
            return self.get_assigned_bo_line()
        return

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get("fiscal_position"),
            )
            self.price_unit = product._get_tax_included_unit_price(
                self.company_id or self.order_id.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                "sale",
                fiscal_position=self.order_id.fiscal_position_id,
                product_price_unit=self._get_display_price(),
                product_currency=self.order_id.currency_id,
            )
        if self.product_id and not self.env.context.get("skip_blanket_find", False):
            return self.get_assigned_bo_line()
        return

    @api.onchange("blanket_order_line")
    def onchange_blanket_order_line(self):
        bol = self.blanket_order_line
        if bol:
            self.product_id = bol.product_id
            if bol.product_uom != self.product_uom:
                price_unit = bol.product_uom._compute_price(
                    bol.price_unit, self.product_uom
                )
            else:
                price_unit = bol.price_unit
            self.price_unit = price_unit
            if bol.taxes_id:
                self.tax_id = bol.taxes_id
        else:
            if not self.tax_id:
                self._compute_tax_id()
            self.with_context(skip_blanket_find=True).product_uom_change()

    @api.constrains("product_id")
    def check_product_id(self):
        for line in self:
            if (
                line.blanket_order_line
                and line.product_id != line.blanket_order_line.product_id
            ):
                raise ValidationError(
                    _(
                        "The product in the blanket order and in the "
                        "sales order must match"
                    )
                )

    @api.constrains("currency_id")
    def check_currency(self):
        for line in self:
            if line.blanket_order_line:
                if line.currency_id != line.blanket_order_line.order_id.currency_id:
                    raise ValidationError(
                        _(
                            "The currency of the blanket order must match with "
                            "that of the sale order."
                        )
                    )
