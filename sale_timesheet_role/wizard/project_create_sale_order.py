# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProjectCreateSaleOrder(models.TransientModel):
    _inherit = 'project.create.sale.order'

    billable_type = fields.Selection(
        selection_add=[
            ('employee_role_rate', 'At Employee/Role Rate')
        ],
    )
    employee_role_ids = fields.One2many(
        string='Employee/Role Lines',
        comodel_name='project.create.sale.order.employee.role.line',
        inverse_name='wizard_id',
    )

    def _make_according_to_billable_type(self, sale_order):
        if self.billable_type == 'employee_role_rate':
            self._make_billable_at_employee_role_rate(sale_order)
        else:
            super()._make_according_to_billable_type(sale_order)

    def _make_billable_at_employee_role_rate(self, sale_order):
        # trying to simulate the SO line created a task, according to the
        # product configuration
        # To avoid, generating a task when confirming the SO
        task_id = self.env['project.task'].search([
            ('project_id', '=', self.project_id.id)
        ], order='create_date DESC', limit=1).id
        project_id = self.project_id.id

        non_billable_tasks = self.project_id.tasks.filtered(
            lambda task: task.billable_type == 'no'
        )

        Map = self.env['project.employee.role.sale.order.line.map']
        map_entries = Map
        SudoMap = Map.sudo()

        # create SO lines: create on SOL per product/price. So many employee
        # can be linked to the same SOL
        SaleOrderLine = self.env['sale.order.line']
        map_product_price_sol = {}  # (product_id, price) --> SOL
        for wizard_line in self.employee_role_ids:
            map_key = (wizard_line.product_id.id, wizard_line.price_unit)
            if map_key not in map_product_price_sol:
                values = {
                    'order_id': sale_order.id,
                    'product_id': wizard_line.product_id.id,
                    'price_unit': wizard_line.price_unit,
                    'product_uom_qty': 0.0,
                }
                if wizard_line.product_id.service_tracking in \
                        ['task_new_project', 'task_global_project']:
                    values['task_id'] = task_id
                if wizard_line.product_id.service_tracking in \
                        ['task_new_project', 'project_only']:
                    values['project_id'] = project_id

                sale_order_line = SaleOrderLine.create(values)
                map_product_price_sol[map_key] = sale_order_line

            map_entries |= SudoMap.create({
                'project_id': self.project_id.id,
                'sale_line_id': map_product_price_sol[map_key].id,
                'employee_id': wizard_line.employee_id.id,
                'role_id': wizard_line.role_id.id,
            })

        # link the project to the SO
        self.project_id.write({
            'sale_order_id': sale_order.id,
            'sale_line_id': sale_order.order_line[0].id,
            'partner_id': self.partner_id.id,
        })
        non_billable_tasks.write({
            'sale_line_id': sale_order.order_line[0].id,
            'partner_id': sale_order.partner_id.id,
            'email_from': sale_order.partner_id.email,
        })

        # assign SOL to timesheets
        unassigned_lines = self.env['account.analytic.line'].search([
            ('task_id', 'in', self.project_id.tasks.ids),
            ('so_line', '=', False),
        ])
        for unassigned_line in unassigned_lines:
            so_line = unassigned_line._timesheet_get_sale_line()
            unassigned_line.write({
                'so_line': so_line.id if so_line else False,
            })

        return map_entries


class ProjectCreateSaleOrderEmployeeRoleLine(models.TransientModel):
    _name = 'project.create.sale.order.employee.role.line'
    _description = 'Sale Order wizard Employee/Role<>Sale Order Line mapping'
    _order = 'id,create_date'

    wizard_id = fields.Many2one(
        comodel_name='project.create.sale.order',
        required=True
    )
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        help='Employee that has timesheets on the project.',
    )
    role_id = fields.Many2one(
        string='Role',
        comodel_name='project.role',
        domain=lambda self: self._domain_role_id(),
    )
    product_id = fields.Many2one(
        string='Service',
        comodel_name='product.product',
        domain=[
            ('type', '=', 'service'),
            ('invoice_policy', '=', 'delivery'),
            ('service_type', '=', 'timesheet')
        ],
        required=True,
        help=(
            'Product of the sales order item. Must be a service invoiced based'
            ' on timesheets on tasks.'
        ),
    )
    price_unit = fields.Float(
        string='Unit Price',
        default=1.0,
        help='Unit price of the sales order item.',
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        related='product_id.currency_id',
        readonly=False
    )

    _sql_constraints = [
        (
            'employee_or_role_set',
            'CHECK(employee_id IS NOT NULL OR role_id IS NOT NULL)',
            'Employee or Role must be set.'
        ),
        (
            'full_mapping_uniq',
            (
                'EXCLUDE ('
                '    wizard_id WITH =, employee_id WITH =, role_id WITH ='
                ') WHERE ('
                '    employee_id IS NOT NULL AND role_id IS NOT NULL'
                ')'
            ),
            'An employee/role cannot be mapped more than once!'
        ),
        (
            'employee_mapping_uniq',
            (
                'EXCLUDE ('
                '    wizard_id WITH =, employee_id WITH ='
                ') WHERE ('
                '    employee_id IS NOT NULL AND role_id IS NULL'
                ')'
            ),
            'An employee cannot be mapped more than once!'
        ),
        (
            'role_mapping_uniq',
            (
                'EXCLUDE ('
                '    wizard_id WITH =, role_id WITH ='
                ') WHERE ('
                '    employee_id IS NULL AND role_id IS NOT NULL'
                ')'
            ),
            'A role cannot be mapped more than once!'
        ),
    ]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price

    @api.model
    def _domain_role_id(self):
        company_id = self._context.get(
            'company_id',
            self.env.user.company_id.id
        )
        return [('company_id', 'in', [False, company_id])]
