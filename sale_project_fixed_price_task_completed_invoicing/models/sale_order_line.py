# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        line = super(SaleOrderLine, self).create(vals)
        if (line.state == 'sale' and not line.order_id.project_id and
                line.product_id.track_service in ('completed_task', )):
            line.order_id._create_analytic_account()
        return line

    @api.constrains('product_id')
    def _onchange_product_id(self):
        for line in self:
            if ('completed_task' == line.product_id.track_service and
                    line.product_uom_qty != 1.0):
                raise ValidationError(_("The quantity for 'Complete Task' "
                                        "products must be exactly one"))

    @api.multi
    def _check_delivered_qty(self):
        for line in self:
            tasks_count = self.env['project.task'].search_count(
                [('sale_line_id', '=', line.id)])
            task_invoiced_count = self.env['project.task'].search_count(
                [('sale_line_id', '=', line.id), ('invoiceable', '=', True)])
            if tasks_count == task_invoiced_count:
                line.qty_delivered = 1.0
