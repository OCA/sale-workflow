# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProjectEmployeeRoleSaleOrderLineMap(models.Model):
    _name = 'project.employee.role.sale.order.line.map'
    _description = 'Project Employee/Role<>Sale Order Line mapping'

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        required=True,
        default=lambda self: self._default_project_id(),
        domain=[('billable_type', '!=', 'no')],
    )
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
    )
    role_id = fields.Many2one(
        string='Role',
        comodel_name='project.role',
        domain=lambda self: self._domain_role_id(),
    )
    sale_line_id = fields.Many2one(
        string='Sale Order Item',
        comodel_name='sale.order.line',
        required=True,
        domain=[('is_service', '=', True)],
    )
    price_unit = fields.Float(related='sale_line_id.price_unit')
    currency_id = fields.Many2one(related='sale_line_id.currency_id')

    @api.model
    def _default_project_id(self):
        return self._context.get('active_id', False)

    @api.model
    def _domain_role_id(self):
        company_id = self._context.get(
            'company_id',
            self.env.user.company_id.id
        )
        return [('company_id', 'in', [False, company_id])]

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
                '    project_id WITH =, employee_id WITH =, role_id WITH ='
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
                '    project_id WITH =, employee_id WITH ='
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
                '    project_id WITH =, role_id WITH ='
                ') WHERE ('
                '    employee_id IS NULL AND role_id IS NOT NULL'
                ')'
            ),
            'A role cannot be mapped more than once!'
        ),
    ]
