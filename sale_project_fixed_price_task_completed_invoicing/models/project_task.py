# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    invoiceable = fields.Boolean(
        string='Invoiceable',
    )
    fixed_price = fields.Boolean(
        string='Fixed Price',
    )

    @api.multi
    def toggle_invoiceable(self):
        for task in self:
            # We dont' want to modify when the related SOLine is invoiced
            if (not task.sale_line_id or
               task.sale_line_id.state in ('done', 'cancel')):
                raise UserError(_("You cannot modify the status if there is "
                                  "no Sale Order Line or if it has been "
                                  "invoiced."))
            task.invoiceable = not task.invoiceable
            task.sale_line_id._check_delivered_qty()

    @api.multi
    def write(self, vals):
        for task in self:
            if (vals.get('sale_line_id') and
               task.sale_line_id.state in ('done', 'cancel')):
                raise ValidationError(_('You cannot modify the Sale Order '
                                        'Line of the task once it is invoiced')
                                      )
        return super(ProjectTask, self).write(vals)

    def create(self, vals):
        SOLine = self.env['sale.order.line']
        so_line = SOLine.browse(vals.get('sale_line_id'))
        # We don't want to add a project.task to an already invoiced line
        if so_line and so_line.state in ('done', 'cancel'):
            raise ValidationError(_('You cannot add a task to and invoiced '
                                    'Sale Order Line'))
        return super(ProjectTask, self).create(vals)

    @api.onchange('invoiceable')
    def _onchange_invoiceable(self):
        for task in self:
            if not task.invoiceable:
                continue
            task.sale_line_id._check_delivered_qty()
