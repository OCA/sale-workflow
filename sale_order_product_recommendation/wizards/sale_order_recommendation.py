# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tests import Form
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class SaleOrderRecommendation(models.TransientModel):
    _name = "sale.order.recommendation"
    _description = "Recommended products for current sale order"

    order_id = fields.Many2one(
        "sale.order",
        "Sale Order",
        default=lambda self: self._default_order_id(),
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    months = fields.Float(
        default=6,
        required=True,
        help="Consider these months backwards to generate recommendations.",
    )
    line_ids = fields.One2many(
        "sale.order.recommendation.line", "wizard_id", "Products"
    )
    line_amount = fields.Integer(
        "Number of recommendations",
        default=15,
        required=True,
        help="The less, the faster they will be found.",
    )
    last_compute = fields.Char()
    # Get default value from config settings
    sale_recommendation_price_origin = fields.Selection(
        [("pricelist", "Pricelist"), ("last_sale_price", "Last sale price")],
        string="Product price origin",
        default="pricelist",
    )
    use_delivery_address = fields.Boolean(string="Use delivery address")

    @api.model
    def _default_order_id(self):
        return self.env.context.get("active_id", False)

    def _extended_recommendable_sale_order_lines_domain(self):
        """Extra domain to include or exclude SO lines"""
        return safe_eval(self.env.user.company_id.sale_line_recommendation_domain)

    def _recommendable_sale_order_lines_domain(self):
        """Domain to find recent SO lines."""
        start = datetime.now() - timedelta(days=self.months * 30)
        start = fields.Datetime.to_string(start)
        partner = (
            self.order_id.partner_shipping_id
            if self.use_delivery_address
            else self.order_id.partner_id.commercial_partner_id
        )
        sale_order_partner_field = (
            "partner_shipping_id" if self.use_delivery_address else "partner_id"
        )
        # Search with sudo for get sale order from other commercials users
        other_sales = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.order_id.company_id.id),
                    (sale_order_partner_field, "child_of", partner.id),
                    ("date_order", ">=", start),
                ]
            )
        )
        domain = [
            ("order_id", "in", (other_sales - self.order_id).ids),
            ("product_id.active", "=", True),
            ("product_id.sale_ok", "=", True),
            ("qty_delivered", "!=", 0.0),
        ]
        # Exclude delivery products
        # We can not use the method _is_delivery() from sale module because we are
        # doing a domain for a readgroup query
        if "is_delivery" in self.env["sale.order.line"]._fields:
            domain.append(("is_delivery", "=", False))
        extended_domain = self._extended_recommendable_sale_order_lines_domain()
        domain = expression.AND([domain, extended_domain])
        return domain

    def _prepare_recommendation_line_vals(self, group_line, so_line=False):
        """Return the vals dictionary for creating a new recommendation line.
        @param group_line: Dictionary returned by the read_group operation.
        @param so_line: Optional sales order line
        """
        vals = {
            "product_id": group_line["product_id"][0],
            "times_delivered": group_line.get("product_id_count", 0),
            "units_delivered": group_line.get("qty_delivered", 0),
        }
        if so_line:
            vals["units_included"] = so_line.product_uom_qty
            vals["sale_line_id"] = so_line.id
        return vals

    @api.onchange("order_id", "months", "line_amount", "use_delivery_address")
    def _generate_recommendations(self):
        """Generate lines according to context sale order."""
        last_compute = "{}-{}-{}-{}".format(
            self.id, self.months, self.line_amount, self.use_delivery_address
        )
        # Avoid execute onchange as times as fields in api.onchange
        # ORM must control this?
        if self.last_compute == last_compute:
            return
        self.last_compute = last_compute
        # Search delivered products in previous months
        # Search with sudo for get sale order from other commercials users
        found_lines = (
            self.env["sale.order.line"]
            .sudo()
            .read_group(
                self._recommendable_sale_order_lines_domain(),
                ["product_id", "qty_delivered"],
                ["product_id"],
            )
        )
        # Manual ordering that circumvents ORM limitations
        found_lines = sorted(
            found_lines,
            key=lambda res: (res["product_id_count"], res["qty_delivered"]),
            reverse=True,
        )
        found_dict = {product["product_id"][0]: product for product in found_lines}
        recommendation_lines = self.env["sale.order.recommendation.line"]
        existing_product_ids = set()
        # Always recommend all products already present in the linked SO except delivery
        # carrier products
        for line in self.order_id.order_line.filtered(lambda ln: not ln._is_delivery()):
            found_line = found_dict.get(
                line.product_id.id,
                {
                    "product_id": (line.product_id.id, False),
                },
            )
            new_line = recommendation_lines.new(
                self._prepare_recommendation_line_vals(found_line, line)
            )
            recommendation_lines += new_line
            existing_product_ids.add(line.product_id.id)
        # Add recent SO recommendations too
        i = 0
        for line in found_lines:
            if line["product_id"][0] in existing_product_ids:
                continue
            new_line = recommendation_lines.new(
                self._prepare_recommendation_line_vals(line)
            )
            recommendation_lines += new_line
            # limit number of results. It has to be done here, as we need to
            # populate all results first, for being able to select best matches
            i += 1
            if i >= self.line_amount:
                break
        self.line_ids = recommendation_lines.sorted(
            key=lambda x: x.times_delivered, reverse=True
        )

    def action_accept(self):
        """Propagate recommendations to sale order."""
        sequence = max(self.order_id.mapped("order_line.sequence") or [0])
        order_form = Form(self.order_id.sudo())
        to_remove = []
        force_zero_units_included = self.env.user.company_id.force_zero_units_included
        for wiz_line in self.line_ids:
            if (
                not wiz_line.sale_line_id
                and not wiz_line.units_included
                and not force_zero_units_included
            ):
                continue
            if wiz_line.sale_line_id:
                index = self.order_id.order_line.ids.index(wiz_line.sale_line_id.id)
                if wiz_line.units_included or force_zero_units_included:
                    with order_form.order_line.edit(index) as line_form:
                        wiz_line._prepare_update_so_line(line_form)
                else:
                    to_remove.append(index)
            else:
                sequence += 1
                with order_form.order_line.new() as line_form:
                    wiz_line._prepare_new_so_line(line_form, sequence)
        # Remove at the end and in reverse order for not having problems
        to_remove.reverse()
        for index in to_remove:
            order_form.order_line.remove(index)
        order_form.save()


class SaleOrderRecommendationLine(models.TransientModel):
    _name = "sale.order.recommendation.line"
    _description = "Recommended product for current sale order"
    _order = "id"

    currency_id = fields.Many2one(related="product_id.currency_id")
    partner_id = fields.Many2one(related="wizard_id.order_id.partner_id")
    product_id = fields.Many2one("product.product", string="Product")
    price_unit = fields.Monetary(compute="_compute_price_unit")
    pricelist_id = fields.Many2one(related="wizard_id.order_id.pricelist_id")
    times_delivered = fields.Integer(readonly=True)
    units_delivered = fields.Float(readonly=True)
    units_included = fields.Float()
    wizard_id = fields.Many2one(
        "sale.order.recommendation",
        "Wizard",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    sale_line_id = fields.Many2one(comodel_name="sale.order.line")
    sale_uom_id = fields.Many2one(related="sale_line_id.product_uom")

    @api.depends(
        "partner_id",
        "product_id",
        "pricelist_id",
        "units_included",
        "wizard_id.sale_recommendation_price_origin",
    )
    def _compute_price_unit(self):
        """
        Get product price unit from product list price or from last sale price
        """
        price_origin = (
            fields.first(self).wizard_id.sale_recommendation_price_origin or "pricelist"
        )
        for line in self:
            if price_origin == "pricelist":
                line.price_unit = line._get_unit_price_from_pricelist()
            else:
                line.price_unit = line._get_last_sale_price_product()

    def _prepare_update_so_line(self, line_form):
        """So we can extend SO update"""
        line_form.product_uom_qty = self.units_included

    def _prepare_new_so_line(self, line_form, sequence):
        """So we can extend SO create"""
        line_form.product_id = self.product_id
        line_form.sequence = sequence
        line_form.product_uom_qty = self.units_included
        if self.wizard_id.sale_recommendation_price_origin == "last_sale_price":
            line_form.price_unit = self.price_unit

    def _get_last_sale_price_product(self):
        """
        Get last price from last order.
        Use sudo to read sale order from other users like as other commercials.
        """
        self.ensure_one()
        so = (
            self.env["sale.order"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.wizard_id.order_id.company_id.id),
                    ("partner_id", "=", self.partner_id.id),
                    ("date_order", "!=", False),
                    ("state", "not in", ("draft", "sent", "cancel")),
                    ("order_line.product_id", "=", self.product_id.id),
                ],
                limit=1,
                order="date_order DESC, id DESC",
            )
        )
        so_line = (
            self.env["sale.order.line"]
            .sudo()
            .search(
                [("order_id", "=", so.id), ("product_id", "=", self.product_id.id)],
                limit=1,
                order="id DESC",
            )
            .with_context(prefetch_fields=False)
        )
        return so_line.price_unit or 0.0

    def _get_unit_price_from_pricelist(self):
        pricelist_rule_id = self.pricelist_id._get_product_rule(
            self.product_id,
            self.units_included or 1.0,
            uom=self.sale_uom_id or self.product_id.uom_id,
            date=self.wizard_id.order_id.date_order,
        )
        pricelist_rule = self.env["product.pricelist.item"].browse(pricelist_rule_id)
        price_rule = pricelist_rule._compute_price(
            self.product_id,
            self.units_included,
            self.sale_uom_id or self.product_id.uom_id,
            self.wizard_id.order_id.date_order,
            currency=self.currency_id,
        )
        price_unit = self.product_id._get_tax_included_unit_price(
            self.wizard_id.order_id.company_id,
            self.currency_id,
            self.wizard_id.order_id.date_order,
            "sale",
            fiscal_position=self.wizard_id.order_id.fiscal_position_id,
            product_price_unit=price_rule,
            product_currency=self.currency_id,
        )
        return price_unit
