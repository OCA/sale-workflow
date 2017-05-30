# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _is_procurement_task(self):
        return (self.product_id.type == 'service' and
                self.product_id.track_service in ('task', 'completed_task'))

    def _create_service_task(self):
        task = super(ProcurementOrder, self)._create_service_task()
        if self.product_id.track_service == 'completed_task':
            task.fixed_price = True
        return task
