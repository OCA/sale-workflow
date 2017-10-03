# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains(
        'state',
        'order_line',
        'order_line.product_id',
        'order_line.product_id.track_service',
    )
    def _check_state(self):
        if self.state == 'sale':
            service_products = self.mapped(
                'order_line.product_id'
            ).filtered(
                lambda p: p.type == 'service'
            )
            track_services = service_products.mapped('track_service')
            if 'user_profile' in track_services:
                if any(s != 'user_profile' for s in track_services):
                    raise ValidationError(_(
                        "With a service product of type 'User profile', "
                        "all service products must have 'User profile' type."
                    ))

    @api.multi
    def action_confirm(self):
        # Copy of the same implementation in sale_timesheet module,
        # but with track_service = 'user_profile'
        result = super(SaleOrder, self).action_confirm()
        for order in self:
            if not order.project_project_id:
                for line in order.order_line:
                    if line.product_id.track_service == 'user_profile':
                        if not order.project_id:
                            order._create_analytic_account(
                                prefix=line.product_id.default_code or None
                            )
                        order.project_id.with_context(
                            # Field added comparing of sale_timesheet module
                            # Not given in the project_create parameters,
                            # because additional values are ignored :(
                            default_project_uses_task_sale_line_map=True
                        ).project_create({
                            'name': order.project_id.name,
                            'use_tasks': True,
                        })
                        break
        return result
