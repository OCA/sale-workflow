# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('state', 'order_line.invoice_status',
                 'order_line.task_ids.invoiceable')
    def _get_invoiced(self):
        super(SaleOrder, self)._get_invoiced()
        for order in self:
            if not all(order.tasks_ids.mapped('invoiceable')):
                order.update({
                    'invoice_status': 'no',
                })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='sale_line_id',
        string='Tasks',
    )

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty',
                 'order_id.state', 'task_ids.invoiceable')
    def _get_to_invoice_qty(self):
        lines = self.filtered(
            lambda x: (x.product_id.type == 'service' and
                       x.product_id.invoicing_finished_task and
                       x.product_id.track_service == 'task')
        )
        for line in lines:
            if all(line.task_ids.mapped('invoiceable')):
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = (
                        line.product_uom_qty - line.qty_invoiced)
                else:
                    line.qty_to_invoice = (
                        line.qty_delivered - line.qty_invoiced)
            else:
                line.qty_to_invoice = 0.0
        super(SaleOrderLine, self - lines)._get_to_invoice_qty()
