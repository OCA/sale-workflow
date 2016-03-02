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
        super(ReportProjectTaskUser, self).init(cr)
        cr.execute("SELECT pg_get_viewdef('report_project_task_user', true)")
        view_def = cr.fetchone()[0]
        # Inject the new field in the expected SQL
        sql = "FROM "
        index = view_def.find(sql)
        if index >= 0:
            sql = ", t.vehicle_id"
            view_def = (view_def[:index] + sql + "\n   " +
                        view_def[index:-1] + sql)
            tools.drop_view_if_exists(cr, 'report_project_task_user')
            cr.execute("CREATE OR REPLACE VIEW report_project_task_user "
                       "AS (%s)" % view_def)
