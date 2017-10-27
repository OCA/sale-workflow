# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleInvoiceGroupMethod(models.Model):
    _name = 'sale.invoice.group.method'
    _description = 'Sale Invoice Group Method'

    name = fields.Char(
        string='Invoice Group',
        required=True,
    )
    criteria_fields_ids = fields.Many2many(
        string='Criteria fields',
        comodel_name='ir.model.fields',
        domain="[('model', '=', 'sale.order')]",
    )
