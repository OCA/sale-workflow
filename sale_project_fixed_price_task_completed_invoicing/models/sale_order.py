# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if not order.project_project_id:
                order._create_analytic_and_tasks()
        return res

    @api.multi
    def _create_analytic_and_tasks(self):
        for order in self:
            for line in order.order_line:
                if (line.product_id.track_service in ('completed_task',
                                                      'timesheet')):
                    if not order.project_id:
                        order._create_analytic_account(
                            prefix=line.product_id.default_code or None)
                    order.project_id.project_create(
                        {'name': order.project_id.name,
                         'use_tasks': True})
