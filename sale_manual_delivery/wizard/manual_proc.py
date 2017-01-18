# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ManualProcurement(models.TransientModel):
    """Creates procurements manually"""
    _name = "manual.procurement"

    date_planned = fields.Date(
        string='Date Planned'
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order TO HIDE',  # TODO HIDE
    )
    line_ids = fields.One2many(
        'manual.line',
        'manual_proc_id',
        string='Lines to validate',
    )
    carrier_id = fields.Many2one(
        'delivery.carrier',
        string='Delivery Method',
    )

    @api.multi
    def record_picking(self):
        for wizard in self:
            ## ---> Set BreakPoint
            import pdb;
            pdb.set_trace()
            carrier_id = wizard.carrier_id
            date_planned = wizard.date_planned
