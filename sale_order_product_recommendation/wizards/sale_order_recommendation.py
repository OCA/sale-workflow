# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import api, fields, models


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
            found_line = found_dict.get(line.product_id.id, {})
            new_line = recommendation_lines.new({
                "product_id": line.product_id.id,
                "times_delivered": found_line.get("product_id_count", 0),
                "units_delivered": found_line.get("qty_delivered", 0),
                "units_included": line.product_uom_qty,
                "sale_line_id": line.id,
            })
            recommendation_lines += new_line
            existing_product_ids.add(line.product_id.id)
        # Add recent SO recommendations too
        i = 0
        for line in found_lines:
            if line["product_id"][0] in existing_product_ids:
                continue
            new_line = recommendation_lines.new({
                "product_id": line["product_id"][0],
                "times_delivered": line["product_id_count"],
                "units_delivered": line["qty_delivered"],
            })
            recommendation_lines += new_line
            # limit number of results. It has to be done here, as we need to
            # populate all results first, for being able to select best matches
            i += 1
            if i >= self.line_amount:
                break
        self.line_ids = recommendation_lines

    def action_accept(self):
        """Propagate recommendations to sale order."""
        so_line_obj = self.env["sale.order.line"]
        so_line_ids = []
        sequence = max(self.order_id.mapped('order_line.sequence') or [0])
        for wiz_line in self.line_ids.filtered('is_modified'):
            # Use preexisting line if any
            if wiz_line.sale_line_id:
                if wiz_line.units_included:
                    wiz_line.sale_line_id.update(
                        wiz_line._prepare_update_so_line())
                    wiz_line.sale_line_id.product_uom_change()
                else:
                    wiz_line.sale_line_id.unlink()
                continue
            sequence += 1
            # Use a new in-memory line otherwise
            so_line = so_line_obj.new(
                wiz_line._prepare_new_so_line(sequence))
            so_line = wiz_line._trigger_so_line_onchanges(so_line)
            so_line_ids.append(so_line.id)
        self.order_id.order_line += so_line_obj.browse(so_line_ids)


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
    is_modified = fields.Boolean()

    @api.depends("partner_id", "product_id", "pricelist_id", "units_included")
    def _compute_price_unit(self):
        for one in self:
            one.price_unit = one.product_id.with_context(
                partner=one.partner_id.id,
                pricelist=one.pricelist_id.id,
                quantity=one.units_included,
            ).price

    @api.onchange("units_included")
    def _onchange_units_included(self):
        self.is_modified = bool(self.sale_line_id or self.units_included)

    def _prepare_update_so_line(self):
        """So we can extend PO update"""
        return {
            "product_uom_qty": self.units_included,
        }

    def _prepare_new_so_line(self, sequence):
        """So we can extend PO create"""
        return {
            "order_id": self.wizard_id.order_id.id,
            "product_id": self.product_id.id,
            "sequence": sequence,
        }

    def _trigger_so_line_onchanges(self, so_line):
        """Extensible method for trigger needed onchanges of the so ling"""
        so_line.product_id_change()
        so_line.product_uom_qty = self.units_included
        so_line.product_uom_change()
        return so_line
