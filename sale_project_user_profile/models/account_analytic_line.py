# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _get_sale_order_line(self, vals=None):
        new_vals = dict(vals or {})

        # If project use mapping for sale line, we continue,
        # else, we just return result of super function
        if self.project_id.project_uses_task_sale_line_map:

            sale_line_map = False

            # 1- We search if we have a mapping for task of the analytic line
            task = self.task_id
            sale_line_map = task.project_user_task_sale_line_map_ids.filtered(
                lambda m: m.user_id == self.user_id
            )

            # 2- If we don't have mapping for the task,
            # we search if we have mapping for user, without tasks
            if not sale_line_map:
                project = self.project_id
                if project.project_uses_task_sale_line_map:
                    sale_line_map = (
                        project.project_user_task_sale_line_map_ids.filtered(
                            lambda m: (
                                m.user_id == self.user_id and
                                not m.task_id
                            )
                        )
                    )

            # 3- If we don't found mapping for the user,
            # we raise a validation error
            if not sale_line_map:
                raise ValidationError(
                    _(
                        'You cannot timesheet on this task. '
                        'Contact the project manager %s'
                    ) % self.project_id.user_id.name
                )

            new_vals['so_line'] = sale_line_map.sale_line_id.id

        return super(AccountAnalyticLine, self)._get_sale_order_line(
            vals=new_vals
        )
