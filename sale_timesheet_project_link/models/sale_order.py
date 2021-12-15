# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    linked_projects_count = fields.Integer(
        compute='_compute_projects_count',
    )

    @api.multi
    def _compute_projects_count(self):
        for rec in self:
            rec.linked_projects_count = len(rec.get_linked_projects())

    @api.multi
    def get_linked_projects(self):
        self.ensure_one()
        return self.order_line.mapped('task_id.project_id') | self.project_ids

    @api.multi
    def action_view_projects_details(self):
        self.ensure_one()
        view_form = (self.env.ref('project.edit_project').id, 'form')
        view_tree = (self.env.ref('project.view_project').id, 'tree')
        linked_projects = self.get_linked_projects()

        action = {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', linked_projects.ids)],
            'view_mode': 'kanban,form',
            'name': _('Projects'),
            'res_model': 'project.project',
        }
        if len(linked_projects) == 1:
            action.update({
                'res_id': linked_projects[0].id,
                'view_mode': 'form',
                'views':  [view_form],
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'views':  [view_tree, view_form],
            })
        return action
