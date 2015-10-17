# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields
from openerp import tools


class ReportProjectTaskUser(models.Model):
    _inherit = 'report.project.task.user'

    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle', string='Vehicle', readonly=True)

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_project_task_user')
        cr.execute("""
            CREATE view report_project_task_user as
              SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.date_start as date_start,
                    t.date_end as date_end,
                    t.date_last_stage_update as date_last_stage_update,
                    t.date_deadline as date_deadline,
                    abs((extract('epoch' from
                    (t.write_date-t.date_start)))/(3600*24))  as no_of_days,
                    t.user_id,
                    t.reviewer_id,
                    progress as progress,
                    t.project_id,
                    t.effective_hours as hours_effective,
                    t.priority,
                    t.name as name,
                    t.company_id,
                    t.partner_id,
                    t.stage_id as stage_id,
                    t.kanban_state as state,
                    remaining_hours as remaining_hours,
                    total_hours as total_hours,
                    t.delay_hours as hours_delay,
                    planned_hours as hours_planned,
                    (extract('epoch' from (t.write_date-t.create_date)))/
                        (3600*24) as closing_days,
                    (extract('epoch' from (t.date_start-t.create_date)))/
                        (3600*24)  as opening_days,
                    (extract('epoch' from (t.date_deadline-(now() at time
                        zone 'UTC'))))/(3600*24)  as delay_endings_days,
                    t.vehicle_id
              FROM project_task t
                WHERE t.active = 'true'
                GROUP BY
                    t.id,
                    remaining_hours,
                    t.effective_hours,
                    progress,
                    total_hours,
                    planned_hours,
                    hours_delay,
                    create_date,
                    write_date,
                    date_start,
                    date_end,
                    date_deadline,
                    date_last_stage_update,
                    t.user_id,
                    t.reviewer_id,
                    t.project_id,
                    t.priority,
                    name,
                    t.company_id,
                    t.partner_id,
                    stage_id,
                    t.vehicle_id
        """)
