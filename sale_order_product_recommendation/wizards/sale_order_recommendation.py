# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
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
    # Get default value from config settings
    sale_recommendation_price_origin = fields.Selection(
        [("pricelist", "Pricelist"), ("last_sale_price", "Last sale price")],
        string="Product price origin",
        default="pricelist",
    )
    use_delivery_address = fields.Boolean(string="Use delivery address")
    recommendations_order = fields.Selection(
        [
            ("times_delivered desc", "Times delivered"),
            ("units_delivered desc", "Units delivered"),
            ("product_categ_complete_name asc", "Product category"),
            ("product_default_code asc", "Product code"),
            ("product_name asc", "Product name"),
        ],
        required=True,
        default="times_delivered desc",
    )

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

    def _reopen_wizard(self):
        """Tell the client to close the wizard and open it again."""
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_reset(self):
        """Empty the list of recommendations."""
        self.line_ids = False
        return self._reopen_wizard()

    def generate_recommendations(self):
        """Generate lines according to context sale order."""
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
        # Sort recommendations by user choice
        order_field, order_dir = map(str.lower, self.recommendations_order.split())
        # Priority order (which can have an str value "0" or "1") must always
        # default to DESC, no matter the order_dir; so we inverse it if it's ASC
        priority_multiplier = 1 if order_dir == "desc" else -1
        self.line_ids = recommendation_lines.sorted(
            key=lambda line: (
                "" if line[order_field] is False else line[order_field],
                int(line.product_id.priority) * priority_multiplier,
            ),
            reverse=order_dir == "desc",
        )
        if not self.line_ids:
            raise UserError(
                _("Nothing found! Modify your criteria or fill the order manually.")
            )
        # Reopen wizard
        return self._reopen_wizard()

    def action_accept(self):
        """Propagate recommendations to sale order."""
        sequence = max(self.order_id.mapped("order_line.sequence") or [0])
        to_remove = []
        sale_order_line_obj = self.env["sale.order.line"].sudo()
        new_line_vals = []
        force_zero_units_included = self.env.user.company_id.force_zero_units_included
        for wiz_line in self.line_ids:
            if (
                not wiz_line.sale_line_id
                and not wiz_line.units_included
                and not force_zero_units_included
            ):
                continue
            if wiz_line.sale_line_id:
                if wiz_line.units_included or force_zero_units_included:
                    wiz_line.sale_line_id.update(
                        wiz_line._prepare_update_so_line_vals()
                    )
                else:
                    to_remove.append(wiz_line.sale_line_id.id)
            else:
                sequence += 1
                vals = wiz_line._prepare_new_so_line_vals(sequence)
                new_line_vals.append(vals)
        # Remove at the end and in reverse order for not having problems
        to_remove.reverse()
        sale_order_line_obj.browse(to_remove).unlink()
        if new_line_vals:
            sale_order_line_obj.create(new_line_vals)


class SaleOrderRecommendationLine(models.TransientModel):
    _name = "sale.order.recommendation.line"
    _description = "Recommended product for current sale order"
    _order = "product_priority desc, id"

    currency_id = fields.Many2one(related="product_id.currency_id")
    partner_id = fields.Many2one(related="wizard_id.order_id.partner_id")
    product_id = fields.Many2one("product.product", string="Product")
    product_name = fields.Char(
        name="Product name", related="product_id.name", readonly=True, store=True
    )
    product_categ_complete_name = fields.Char(
        string="Product category",
        related="product_id.categ_id.complete_name",
        readonly=True,
        store=True,
    )
    product_default_code = fields.Char(
        related="product_id.default_code", readonly=True, store=True
    )
    product_priority = fields.Selection(
        related="product_id.priority", store=True, readonly=False
    )
    product_uom_readonly = fields.Boolean(related="sale_line_id.product_uom_readonly")
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id", depends=["product_id"]
    )
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
    sale_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        compute="_compute_sale_uom_id",
        store=True,
        readonly=False,
        domain="[('category_id', '=', product_uom_category_id)]",
    )

    @api.depends("sale_line_id", "product_id")
    def _compute_sale_uom_id(self):
        for line in self:
            line.sale_uom_id = line.sale_line_id.product_uom or line.product_id.uom_id

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

    def _prepare_update_so_line_vals(self):
        vals = {"product_uom_qty": self.units_included}
        if not self.product_uom_readonly:
            vals["product_uom"] = self.sale_uom_id.id
        return vals

    def _prepare_new_so_line_vals(self, sequence):
        vals = {
            "product_id": self.product_id.id,
            "sequence": sequence,
            "product_uom_qty": self.units_included,
            "order_id": self.wizard_id.order_id.id,
        }
        if not self.product_uom_readonly:
            vals["product_uom"] = self.sale_uom_id.id
        if self.wizard_id.sale_recommendation_price_origin == "last_sale_price":
            vals["price_unit"] = self.price_unit
        return vals

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
