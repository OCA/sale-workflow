# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities')],
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        help='Ordered Quantity: Invoice based on the quantity the customer '
             'ordered.\n'
             'Delivered Quantity: Invoiced based on the quantity the vendor '
             'delivered (time or deliveries).')
