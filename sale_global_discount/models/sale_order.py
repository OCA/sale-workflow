# Copyright 2020 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    global_discount_ids = fields.Many2many(
        comodel_name="global.discount",
        string="Sale Global Discounts",
        domain="[('discount_scope', '=', 'sale'), "
        "('account_id', '!=', False), '|', "
        "('company_id', '=', company_id), ('company_id', '=', False)]",
        compute="_compute_global_discount_ids",
        store=True,
        readonly=False,
    )
    # HACK: Looks like UI doesn't behave well with Many2many fields and
    # negative groups when the same field is shown. In this case, we want to
    # show the readonly version to any not in the global discount group.
    # TODO: Check if it's fixed in future versions
    global_discount_ids_readonly = fields.Many2many(
        related="global_discount_ids",
        string="Sale Global Discounts (readonly)",
        readonly=True,
    )
    amount_global_discount = fields.Monetary(
        string="Total Global Discounts",
        compute="_compute_amounts",  # pylint: disable=C8108
        currency_field="currency_id",
        compute_sudo=True,  # Odoo core fields are storable so compute_sudo is True
        readonly=True,
        store=True,
    )
    amount_untaxed_before_global_discounts = fields.Monetary(
        string="Amount Untaxed Before Discounts",
        compute="_compute_amounts",  # pylint: disable=C8108
        currency_field="currency_id",
        compute_sudo=True,  # Odoo core fields are storable so compute_sudo is True
        readonly=True,
        store=True,
    )
    amount_total_before_global_discounts = fields.Monetary(
        string="Amount Total Before Discounts",
        compute="_compute_amounts",  # pylint: disable=C8108
        currency_field="currency_id",
        compute_sudo=True,  # Odoo core fields are storable so compute_sudo is True
        readonly=True,
        store=True,
    )

    @api.model
    def get_discounted_global(self, price=0, discounts=None):
        if not discounts:
            return price
        discounted_price = price
        for discount in discounts:
            discounted_price *= 1 - (discount / 100)
        return discounted_price

    def _check_global_discounts_sanity(self):
        """Perform a sanity check for discarding cases that will lead to
        incorrect data in discounts.
        """
        self.ensure_one()
        if not self.global_discount_ids:
            return True
        taxes_keys = {}
        for line in self.order_line.filtered(
            lambda _line: not _line.display_type and _line.product_id
        ):
            if not line.tax_id:
                raise exceptions.UserError(
                    _("With global discounts, taxes in lines are required.")
                )
            for key in taxes_keys:
                if key == line.tax_id:
                    break
                elif key & line.tax_id:
                    raise exceptions.UserError(
                        _("Incompatible taxes found for global discounts.")
                    )
            else:
                taxes_keys[line.tax_id] = True

    @api.depends(
        "order_line.product_id.bypass_global_discount",
        "order_line.price_subtotal",
        "order_line.price_tax",
        "order_line.price_total",
        "global_discount_ids",
    )
    def _compute_amounts(self):
        res = super()._compute_amounts()
        for order in self:
            order._check_global_discounts_sanity()
            amount_untaxed_before_global_discounts = order.amount_untaxed
            amount_total_before_global_discounts = order.amount_total
            discounts = order.global_discount_ids.mapped("discount")
            amount_discounted_untaxed = amount_discounted_tax = 0
            for line in order.order_line:
                discounted_subtotal = line.price_subtotal
                if not line.product_id.bypass_global_discount:
                    discounted_subtotal = self.get_discounted_global(
                        line.price_subtotal, discounts.copy()
                    )
                amount_discounted_untaxed += discounted_subtotal
                discounted_tax = line.tax_id.compute_all(
                    discounted_subtotal,
                    line.order_id.currency_id,
                    1.0,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )
                amount_discounted_tax += sum(
                    t.get("amount", 0.0) for t in discounted_tax.get("taxes", [])
                )
            order.update(
                {
                    "amount_untaxed_before_global_discounts": (
                        amount_untaxed_before_global_discounts
                    ),
                    "amount_total_before_global_discounts": (
                        amount_total_before_global_discounts
                    ),
                    "amount_global_discount": (
                        amount_untaxed_before_global_discounts
                        - amount_discounted_untaxed
                    ),
                    "amount_untaxed": amount_discounted_untaxed,
                    "amount_tax": amount_discounted_tax,
                    "amount_total": (amount_discounted_untaxed + amount_discounted_tax),
                }
            )
        return res

    def _compute_tax_totals(self):
        res = super()._compute_tax_totals()
        for order in self:
            amount_discount_by_group = {}
            cumulative_discount_rate = 1.0
            # Calculate cumulative discount rate
            for gbl_disc in order.global_discount_ids:
                discount_rate = gbl_disc.discount / 100
                cumulative_discount_rate *= 1 - discount_rate
            amount_untaxed = 0.0
            # Calculate the total discount amount and discount by tax group
            for line in order.order_line:
                if line.display_type or not line.product_id:
                    continue
                # Apply cumulative discount rate only if bypass_global_discount is False
                if not line.product_id.bypass_global_discount:
                    discounted_price_subtotal = (
                        line.price_subtotal * cumulative_discount_rate
                    )
                else:
                    discounted_price_subtotal = line.price_subtotal
                amount_untaxed += discounted_price_subtotal
                # Calculate tax amounts for each tax group based on the
                # discounted subtotal
                for tax in line.tax_id:
                    tax_group_id = tax.tax_group_id.id
                    if tax_group_id not in amount_discount_by_group:
                        amount_discount_by_group[tax_group_id] = 0.0
                    # Calculate correct base amount for tax computation
                    base_amount = discounted_price_subtotal
                    # Compute taxes on the correct base amount
                    discounted_tax_vals = tax.compute_all(
                        base_amount,
                        order.currency_id,
                        1.0,
                        product=line.product_id,
                        partner=order.partner_shipping_id,
                    )
                    total_discounted_tax = sum(
                        t.get("amount", 0.0)
                        for t in discounted_tax_vals.get("taxes", [])
                    )
                    amount_discount_by_group[tax_group_id] += total_discounted_tax
            # Calculate the final amount total
            amount_total = amount_untaxed + sum(amount_discount_by_group.values())
            order.tax_totals["amount_untaxed"] = amount_untaxed
            order.tax_totals["amount_total"] = amount_total
            order.tax_totals["formatted_amount_untaxed"] = formatLang(
                self.env, amount_untaxed, currency_obj=order.currency_id
            )
            order.tax_totals["formatted_amount_total"] = formatLang(
                self.env, amount_total, currency_obj=order.currency_id
            )
            # Update groups by subtotal
            for group in order.tax_totals["groups_by_subtotal"].values():
                for tax_group in group:
                    tax_group_id = tax_group["tax_group_id"]
                    discount_for_group = amount_discount_by_group.get(tax_group_id, 0.0)
                    tax_group["tax_group_amount"] = discount_for_group
                    tax_group["formatted_tax_group_amount"] = formatLang(
                        self.env,
                        tax_group["tax_group_amount"],
                        currency_obj=order.currency_id,
                    )
            # Update subtotals
            for subtotal in order.tax_totals["subtotals"]:
                subtotal["amount"] = amount_untaxed
                subtotal["formatted_amount"] = formatLang(
                    self.env, amount_untaxed, currency_obj=order.currency_id
                )
        return res

    @api.depends("partner_id", "company_id")
    def _compute_global_discount_ids(self):
        for order in self:
            commercial = order.partner_id.commercial_partner_id
            commercial_global_disc = commercial.customer_global_discount_ids
            partner_global_disc = order.partner_id.customer_global_discount_ids
            discounts = self.env["global.discount"]
            _discounts = self.env["global.discount"]
            if partner_global_disc:
                _discounts = partner_global_disc
            else:
                _discounts = commercial_global_disc
            for discount in _discounts:
                if discount.company_id == order.company_id:
                    discounts |= discount
            order.global_discount_ids = discounts

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.global_discount_ids:
            invoice_vals.update(
                {"global_discount_ids": [(6, 0, self.global_discount_ids.ids)]}
            )
        return invoice_vals
