# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    manual_billable_type = fields.Selection(
        selection=lambda self: self._selection_proxied_billable_type(),
    )
    proxied_billable_type = fields.Selection(
        string='Billing Type',
        selection=lambda self: self._selection_proxied_billable_type(),
        compute='_compute_proxied_billable_type',
        inverse='_inverse_proxied_billable_type',
        help=(
            'Billing type selection. Unset and save to auto-detect billing'
            ' type.'
        ),
    )

    @api.multi
    @api.depends('billable_type')
    def _compute_proxied_billable_type(self):
        for project in self:
            if project.billable_type == 'no':
                project.proxied_billable_type = None
            elif not project.proxied_billable_type:
                project.proxied_billable_type = project.billable_type

    @api.multi
    def _inverse_proxied_billable_type(self):
        for project in self:
            project.manual_billable_type = project.proxied_billable_type

    @api.multi
    @api.constrains('manual_billable_type', 'billable_type')
    def _check_billing_types(self):
        for project in self:
            if project.billable_type == 'no' and project.manual_billable_type:
                raise ValidationError(_(
                    'Setting manual Billing Type is not allowed on'
                    ' non-billable projects.'
                ))

    @api.multi
    @api.depends('manual_billable_type')
    def _compute_billable_type(self):
        result = super()._compute_billable_type()

        for project in self:
            if project.billable_type != 'no' and \
                    project.manual_billable_type and \
                    project.billable_type != project.manual_billable_type:
                project.billable_type = project.manual_billable_type

        return result

    @api.onchange('proxied_billable_type')
    def _onchange_proxied_billable_type(self):
        if not self.proxied_billable_type and self.billable_type != 'no':
            self.proxied_billable_type = self.billable_type
        else:
            self.manual_billable_type = self.proxied_billable_type

    @api.onchange('sale_line_employee_ids', 'billable_type')
    def _onchange_sale_line_employee_ids(self):
        """ Override the behaviour to avoid billable_type auto-determination
            and side effects
        """
        pass

    @api.model
    def _selection_proxied_billable_type(self):
        return list(filter(
            lambda x: x[0] != 'no',
            self._fields['billable_type'].selection
        ))
