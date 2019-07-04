# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    amount_delivered_from_task = fields.Monetary(
        string='Delivered from task',
        compute='_compute_amount_delivered_from_task',
        currency_field='currency_id',
    )
    amount_invoiced_from_task = fields.Monetary(
        string='Invoiced from task',
        compute='_compute_amount_invoiced_from_task',
        currency_field='currency_id',
    )
    amount_delivered_from_task_company_currency = fields.Monetary(
        string='Delivered from task (company currency)',
        compute='_compute_amount_delivered_from_task',
        currency_field='company_currency_id',
    )
    amount_invoiced_from_task_company_currency = fields.Monetary(
        string='Invoiced from task (company currency)',
        compute='_compute_amount_invoiced_from_task',
        currency_field='company_currency_id',
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        store=True,
        readonly=True,
        string='Company currency',
    )

    is_company_currency = fields.Boolean(
        compute='_compute_is_company_currency'
    )

    @api.multi
    @api.depends('currency_id', 'company_currency_id')
    def _compute_is_company_currency(self):
        for line in self:
            line.is_company_currency = (
                line.company_currency_id == line.currency_id
            )

    @api.multi
    def _get_timesheet_for_amount_calculation(self, only_invoiced=False):
        """Return all timesheet line related to the sale order line."""
        self.ensure_one()
        if not self.task_id:
            self.amount_delivered_from_task = 0
            return []
        tasks_linked_to_line = self.env['project.task'].search(
            [('sale_line_id', '=', self.id)]
        )
        tasks = self.env['project.task'].search(
            [('id', 'child_of', tasks_linked_to_line.ids)]
        )
        ts = tasks.mapped('timesheet_ids').filtered('employee_id')
        if only_invoiced:
            ts = ts.filtered(
                lambda r: r.timesheet_invoice_id
                and r.timesheet_invoice_id.state != 'cancel'
            )
        return ts

    @api.multi
    @api.depends(
        'task_id',
        'task_id.timesheet_ids.timesheet_invoice_id',
        'task_id.timesheet_ids.unit_amount',
    )
    def _compute_amount_delivered_from_task(self):
        for line in self:
            total = 0
            for ts in line._get_timesheet_for_amount_calculation():
                rate_line = ts.project_id.sale_line_employee_ids.filtered(
                    lambda r: r.employee_id == ts.employee_id
                )
                total += ts.unit_amount * rate_line.price_unit
            line.amount_delivered_from_task = total
            line.amount_delivered_from_task_company_currency = (
                total * line.order_id.currency_rate
            )

    @api.multi
    @api.depends(
        'task_id',
        'task_id.timesheet_ids.timesheet_invoice_id',
        'task_id.timesheet_ids.unit_amount',
    )
    def _compute_amount_invoiced_from_task(self):
        for line in self:
            total = 0
            for ts in line._get_timesheet_for_amount_calculation(True):
                rate_line = ts.project_id.sale_line_employee_ids.filtered(
                    lambda r: r.employee_id == ts.employee_id
                )
                total += ts.unit_amount * rate_line.price_unit
            line.amount_invoiced_from_task = total
            line.amount_invoiced_from_task_company_currency = (
                total * line.order_id.currency_rate
            )

    @api.multi
    @api.depends('amount_delivered_from_task', 'product_uom_qty', 'price_unit')
    def _compute_qty_delivered(self):
        """Change quantity delivered for line with a product milestone."""
        super()._compute_qty_delivered()
        for line in self:
            if line._is_linked_to_milestone_product():
                if line.price_unit:
                    line.qty_delivered = (
                        line.product_uom_qty
                        * line.amount_delivered_from_task
                        / (line.price_unit)
                    )
                else:
                    line.qty_delivered = 0.

    @api.multi
    @api.depends('amount_invoiced_from_task', 'product_uom_qty', 'price_unit')
    def _get_invoice_qty(self):
        """Change quantity invoiced for line with a product milestone."""
        super()._get_invoice_qty()
        for line in self:
            if line._is_linked_to_milestone_product():
                if line.price_unit:
                    line.qty_invoiced = (
                        line.product_uom_qty
                        * line.amount_invoiced_from_task
                        / line.price_unit
                    )
                else:
                    line.qty_invoiced = 0.

    @api.multi
    def _is_linked_to_milestone_product(self):
        self.ensure_one()
        return (
            self.product_id.type == 'service'
            and self.product_id.service_policy == 'delivered_manual'
            and self.product_id.service_tracking == 'task_new_project'
        )

    @api.multi
    def _compute_invoice_status(self):
        """Change invoice status for milestone line"""
        super()._compute_invoice_status()
        for line in self:
            if line._is_linked_to_milestone_product():
                mapping = line.project_id.sale_line_employee_ids.filtered(
                    lambda r: r.sale_line_id == line
                )
                if not mapping:
                    if line.qty_delivered <= line.product_uom_qty:
                        line.invoice_status = 'no'
                    else:
                        line.invoice_status = 'upselling'
