# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    invoiceable = fields.Boolean(
        string='Invoiceable',
    )


class ProjectTask(models.Model):
    _inherit = 'project.task'

    invoiceable = fields.Boolean(
        string='Invoiceable',
    )
    invoicing_finished_task = fields.Boolean(
        related='sale_line_id.product_id.invoicing_finished_task',
        readonly=True,
    )

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for task in self:
            if task.invoicing_finished_task and \
                    task.stage_id.invoiceable and\
                    not task.invoiceable:
                task.invoiceable = True

    @api.multi
    def toggle_invoiceable(self):
        for task in self:
            # We dont' want to modify when the related SOLine is invoiced
            if (not task.sale_line_id or
                    task.sale_line_id.state in ('done', 'cancel') or
                    task.sale_line_id.invoice_status in ('invoiced',)):
                raise UserError(_("You cannot modify the status if there is "
                                  "no Sale Order Line or if it has been "
                                  "invoiced."))
            task.invoiceable = not task.invoiceable

    @api.multi
    def write(self, vals):
        for task in self:
            if (vals.get('sale_line_id') and
                    task.sale_line_id.state in ('done', 'cancel')):
                raise ValidationError(_('You cannot modify the Sale Order '
                                        'Line of the task once it is invoiced')
                                      )
        res = super(ProjectTask, self).write(vals)
        # Onchange stage_id field is not triggered with statusbar widget
        if 'stage_id' in vals:
            self._onchange_stage_id()
        return res

    @api.model
    def create(self, vals):
        SOLine = self.env['sale.order.line']
        so_line = SOLine.browse(vals.get('sale_line_id'))
        # We don't want to add a project.task to an already invoiced line
        if so_line and so_line.state in ('done', 'cancel'):
            raise ValidationError(_('You cannot add a task to and invoiced '
                                    'Sale Order Line'))
        # Onchange stage_id field is not triggered with statusbar widget
        if 'sale_line_id' in vals and 'stage_id' in vals:
            stage = self.env['project.task.type'].browse(vals['stage_id'])
            if so_line.product_id.invoicing_finished_task and \
                    stage.invoiceable:
                vals['invoiceable'] = True
        return super(ProjectTask, self).create(vals)
