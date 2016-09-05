# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class SaleOrderTypology(models.Model):
    _inherit = 'sale.order.type'
    invoice_type_id = fields.Many2one(
        'sale_journal.invoice.type', 'Invoice Type')
