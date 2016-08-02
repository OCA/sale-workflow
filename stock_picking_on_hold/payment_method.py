# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    hold_picking_until_payment = fields.Boolean(
        string='Hold Picking Until Payment',
        help="If set to true, pickings will not be automatically confirmed"
             "when the invoice has not been paid."
    )
