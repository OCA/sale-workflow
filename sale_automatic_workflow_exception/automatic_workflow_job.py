# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AutomaticWorkflowJob(models.Model):
    _inherit = 'automatic.workflow.job'

    @api.multi
    def _get_domain_for_sale_validation(self):
        res = super(AutomaticWorkflowJob, self).\
            _get_domain_for_sale_validation()
        res.append(('exception_ids', '=', False))
        return res
