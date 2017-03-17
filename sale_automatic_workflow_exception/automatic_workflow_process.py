# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast

from odoo import api, models


class SaleWorkflowprocess(models.Model):
    _inherit = 'sale.workflow.process'

    @api.model
    def _default_filter(self, xmlid):
        res = super(SaleWorkflowprocess, self)._default_filter(xmlid)
        if res and xmlid ==\
                'sale_automatic_workflow.automatic_workflow_order_filter':
            domain = ast.literal_eval(res.domain or "[]")
            domain.extend(['|', ('exception_ids', '=', False),
                           ('ignore_exception', '=', True)])
            res.domain = str(domain)
        return res
