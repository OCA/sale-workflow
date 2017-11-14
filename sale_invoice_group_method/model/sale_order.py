# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_group_method_id = fields.Many2one(
        string='Invoice Group Method',
        comodel_name='sale.invoice.group.method'
    )

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id.invoice_group_method_id:
            self.update(
                {
                    'invoice_group_method_id':
                        self.partner_id.invoice_group_method_id.id,
                }
            )

    @api.model
    def _get_invoice_group_key(self, order):
        res = super(SaleOrder, self)._get_invoice_group_key(order)
        invoice_group_method_fields = \
            order.invoice_group_method_id.criteria_fields_ids
        for method_fields in invoice_group_method_fields:
            res += (order[method_fields.name],)
        res += (order.payment_term_id.id,)
        return res
