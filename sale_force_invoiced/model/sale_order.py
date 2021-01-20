# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    force_invoiced = fields.Boolean(string='Force invoiced',
                                    help='When you set this field, the sales '
                                         'order will be considered as fully '
                                         'invoiced, even when there may be '
                                         'ordered or delivered quantities '
                                         'pending to invoice. To use this '
                                         'field, the invoice must be in '
                                         '"locked" state.',
                                    readonly=True,
                                    states={'done': [('readonly', False)]},
                                    copy=False,
                                    )

    def _get_force_invoiced_allowed_invoice_status(self):
        return ('to invoice',)

    @api.depends('force_invoiced')
    def _get_invoiced(self):
        super(SaleOrder, self)._get_invoiced()
        allowed_status = self._get_force_invoiced_allowed_invoice_status()
        for order in self:
            if (
                order.force_invoiced and
                order.invoice_status in allowed_status
            ):
                order.invoice_status = 'invoiced'
