# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.tests import Form


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
        "sale.order.recommendation.line",
        "wizard_id",
        "Products",
    )
    line_amount = fields.Integer(
        "Number of recommendations",
        default=15,
        required=True,
        help="The less, the faster they will be found.",
    )
    last_compute = fields.Char()
    # Get default value from config settings
    sale_recommendation_price_origin = fields.Selection([
        ('pricelist', 'Pricelist'),
        ('last_sale_price', 'Last sale price')
    ], string="Product price origin", default="pricelist")

    @api.model
    def _default_order_id(self):
        return self.env.context.get("active_id", False)

    def _recomendable_sale_order_lines_domain(self):
        """Domain to find recent SO lines."""
        start = datetime.now() - timedelta(days=self.months * 30)
        start = fields.Datetime.to_string(start)
        other_sales = self.env["sale.order"].search([
            ("partner_id", "child_of",
             self.order_id.partner_id.commercial_partner_id.id),
            ("date_order", ">=", start),
        ])
        return [
            ("order_id", "in", (other_sales - self.order_id).ids),
            ("product_id.active", "=", True),
            ("product_id.sale_ok", "=", True),
            ("qty_delivered", "!=", 0.0),
        ]

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

    @api.onchange("order_id", "months", "line_amount")
    def _generate_recommendations(self):
        """Generate lines according to context sale order."""
        last_compute = '{}-{}-{}'.format(
            self.id, self.months, self.line_amount)
        # Avoid execute onchange as times as fields in api.onchange
        # ORM must control this?
        if self.last_compute == last_compute:
            return
        self.last_compute = last_compute
        # Search delivered products in previous months
        found_lines = self.env["sale.order.line"].read_group(
            self._recomendable_sale_order_lines_domain(),
            ["product_id", "qty_delivered"],
            ["product_id"],
        )
        # Manual ordering that circumvents ORM limitations
        found_lines = sorted(
            found_lines,
            key=lambda res: (
                res["product_id_count"],
                res["qty_delivered"],
            ),
            reverse=True,
        )
        found_dict = {l["product_id"][0]: l for l in found_lines}
        recommendation_lines = self.env["sale.order.recommendation.line"]
        existing_product_ids = set()
        # Always recommend all products already present in the linked SO
        for line in self.order_id.order_line:
            found_line = found_dict.get(line.product_id.id, {
                "product_id": (line.product_id.id, False),
            })
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
            key=lambda x: x.times_delivered,
            reverse=True
        )

    def action_accept(self):
        """Propagate recommendations to sale order."""
        sequence = max(self.order_id.mapped('order_line.sequence') or [0])
        order_form = Form(self.order_id.sudo())
        to_remove = []
        for wiz_line in self.line_ids.filtered(
            lambda x: x.sale_line_id or x.units_included
        ):
            if wiz_line.sale_line_id:
                index = self.order_id.order_line.ids.index(
                    wiz_line.sale_line_id.id)
                if wiz_line.units_included:
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

    currency_id = fields.Many2one(
        related="product_id.currency_id",
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="wizard_id.order_id.partner_id",
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    price_unit = fields.Monetary(
        compute="_compute_price_unit",
    )
    pricelist_id = fields.Many2one(
        related="wizard_id.order_id.pricelist_id",
        readonly=True,
    )
    times_delivered = fields.Integer(
        readonly=True,
    )
    units_delivered = fields.Float(
        readonly=True,
    )
    units_included = fields.Float()
    wizard_id = fields.Many2one(
        "sale.order.recommendation",
        "Wizard",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
    )
    sale_uom_id = fields.Many2one(related="sale_line_id.product_uom")

    @api.depends("partner_id", "product_id", "pricelist_id", "units_included",
                 "wizard_id.sale_recommendation_price_origin")
    def _compute_price_unit(self):
        """
        Get product price unit from product list price or from last sale price
        """
        price_origin = (
            fields.first(self).wizard_id.sale_recommendation_price_origin or
            "pricelist"
        )
        for one in self:
            if price_origin == "pricelist":
                one.price_unit = one.product_id.with_context(
                    partner=one.partner_id.id,
                    pricelist=one.pricelist_id.id,
                    quantity=one.units_included,
                ).price
            else:
                one.price_unit = one._get_last_sale_price_product()

    def _prepare_update_so_line(self, line_form):
        """So we can extend SO update"""
        line_form.product_uom_qty = self.units_included

    def _prepare_new_so_line(self, line_form, sequence):
        """So we can extend SO create"""
        line_form.product_id = self.product_id
        line_form.sequence = sequence
        line_form.product_uom_qty = self.units_included
        if (self.wizard_id.sale_recommendation_price_origin ==
                "last_sale_price"):
            line_form.price_unit = self.price_unit

    def _get_last_sale_price_product(self):
        """
        Get last price from last order.
        Use sudo to read sale order from other users like as other commercials.
        """
        self.ensure_one()
        so = self.env["sale.order"].sudo().search([
            ("company_id", "=", self.env.user.company_id.id),
            ("partner_id", "=", self.partner_id.id),
            ("confirmation_date", "!=", False),
            ("state", "not in", ('draft', 'sent', 'cancel')),
            ("order_line.product_id", "=", self.product_id.id)
        ], limit=1, order="confirmation_date DESC, id DESC")
        so_line = self.env["sale.order.line"].sudo().search([
            ("order_id", "=", so.id),
            ("product_id", "=", self.product_id.id)
        ], limit=1, order="id DESC").with_context(prefetch_fields=False)
        return so_line.price_unit or 0.0
