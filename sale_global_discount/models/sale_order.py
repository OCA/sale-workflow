# Copyright 2020 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    global_discount_ids = fields.Many2many(
        comodel_name='global.discount',
        string='Sale Global Discounts',
        domain="[('discount_scope', '=', 'sale'), "
               "('account_id', '!=', False), '|', "
               "('company_id', '=', company_id), ('company_id', '=', False)]",
    )
    amount_global_discount = fields.Monetary(
        string='Total Global Discounts',
        compute='_amount_all',
        currency_field='currency_id',
        readonly=True,
    )
    amount_untaxed_before_global_discounts = fields.Monetary(
        string='Amount Untaxed Before Discounts',
        compute='_amount_all',
        currency_field='currency_id',
        readonly=True,
    )
    amount_total_before_global_discounts = fields.Monetary(
        string='Amount Total Before Discounts',
        compute='_amount_all',
        currency_field='currency_id',
        readonly=True,
    )

    @api.model
    def get_discounted_global(self, price=0, discounts=None):
        """Compute discounts successively"""
        discounts = discounts or []
        if not discounts:
            return price
        discount = discounts.pop(0)
        price *= 1 - (discount / 100)
        return self.get_discounted_global(price, discounts)

    def _check_global_discounts_sanity(self):
        """Perform a sanity check for discarding cases that will lead to
        incorrect data in discounts.
        """
        self.ensure_one()
        if not self.global_discount_ids:
            return True
        taxes_keys = {}
        for line in self.order_line:
            if not line.tax_id:
                raise exceptions.UserError(_(
                    "With global discounts, taxes in lines are required."
                ))
            for key in taxes_keys:
                if key == line.tax_id:
                    break
                elif key & line.tax_id:
                    raise exceptions.UserError(_(
                        "Incompatible taxes found for global discounts."
                    ))
            else:
                taxes_keys[line.tax_id] = True

    @api.depends('order_line.price_total', 'global_discount_ids')
    def _amount_all(self):
        res = super()._amount_all()
        for order in self:
            order._check_global_discounts_sanity()
            amount_untaxed_before_global_discounts = order.amount_untaxed
            amount_total_before_global_discounts = order.amount_total
            discounts = order.global_discount_ids.mapped('discount')
            amount_discounted_untaxed = amount_discounted_tax = 0
            for line in order.order_line:
                discounted_subtotal = self.get_discounted_global(
                    line.price_subtotal, discounts.copy())
                amount_discounted_untaxed += discounted_subtotal
                discounted_tax = line.tax_id.compute_all(
                    discounted_subtotal, line.order_id.currency_id,
                    1.0, product=line.product_id,
                    partner=line.order_id.partner_shipping_id)
                amount_discounted_tax += sum(
                    t.get('amount', 0.0)
                    for t in discounted_tax.get('taxes', []))
            order.update({
                'amount_untaxed_before_global_discounts': (
                    amount_untaxed_before_global_discounts),
                'amount_total_before_global_discounts': (
                    amount_total_before_global_discounts),
                'amount_global_discount': (
                    amount_untaxed_before_global_discounts -
                    amount_discounted_untaxed),
                'amount_untaxed': amount_discounted_untaxed,
                'amount_tax': amount_discounted_tax,
                'amount_total': (
                    amount_discounted_untaxed + amount_discounted_tax),
            })
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        self.global_discount_ids = (
            self.partner_id.customer_global_discount_ids or
            self.partner_id.commercial_partner_id
            .customer_global_discount_ids)
        return res

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.global_discount_ids:
            invoice_vals.update({
                'global_discount_ids': [(6, 0, self.global_discount_ids.ids)],
            })
        return invoice_vals

    def action_invoice_create(self, grouped=False, final=False):
        res = super().action_invoice_create(grouped=grouped, final=final)
        invoices = self.env['account.invoice'].browse(res)
        invoices._set_global_discounts()
        return res

    def _amount_by_group(self):
        """We can apply discounts directly by tax groups."""
        super()._amount_by_group()
        discounts = self.global_discount_ids.mapped('discount')
        if not discounts:
            return
        round_curr = self.currency_id.round
        for order in self:
            res = []
            for tax in order.amount_by_group:
                tax_amount = round_curr(
                    self.get_discounted_global(tax[1], discounts.copy()))
                tax_base = round_curr(
                    self.get_discounted_global(tax[2], discounts.copy()))
                res.append((tax[0], tax_amount, tax_base, tax[3]))
            order.amount_by_group = res
