# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    sale_merge_draft_invoice = fields.Selection([
        (0, 'Create a new invoice every time a sale order is invoiced'),
        (1, 'Merge new invoices with existing draft ones')],
        string="Invoices",
        related='company_id.sale_merge_draft_invoice',
    )
