# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        prev_values = dict()
        for order in self:
            prev_values.update(order.order_line.triple_discount_preprocess())
        super(SaleOrder, self)._amount_all()
        self.env['sale.order.line'].triple_discount_postprocess(prev_values)

    @api.multi
    def _get_tax_amount_by_group(self):
        # Copy/paste from standard method in sale
        self.ensure_one()
        res = {}
        for line in self.order_line:
            price_reduce = line.price_reduce  # changed
            taxes = line.tax_id.compute_all(
                price_reduce, quantity=line.product_uom_qty,
                product=line.product_id,
                partner=self.partner_shipping_id)['taxes']
            for tax in line.tax_id:
                group = tax.tax_group_id
                res.setdefault(group, 0.0)
                for t in taxes:
                    if (t['id'] == tax.id or
                            t['id'] in tax.children_tax_ids.ids):
                        res[group] += t['amount']
        res = sorted(res.items(), key=lambda l: l[0].sequence)
        res = map(lambda l: (l[0].name, l[1]), res)
        return res

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super(SaleOrder, self).action_invoice_create(
            grouped=grouped, final=final
        )
        invoices = self.env['account.invoice'].browse(invoice_ids)
        for inv in invoices:
            inv._onchange_invoice_line_ids()
        return invoice_ids
