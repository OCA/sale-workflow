# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _prepare_project(self, procurement):
        res = super(ProcurementOrder, self)._prepare_project(procurement)
        sale_order = procurement.sale_line_id.order_id
        if sale_order.vehicle_id:
            vehicle = {'vehicle_id': sale_order.vehicle_id.id}
            res.update(vehicle)
        return res

    @api.model
    def _prepare_task(self, procurement):
        res = super(ProcurementOrder, self)._prepare_task(procurement)
        sale_order = procurement.sale_line_id.order_id
        if sale_order.vehicle_id:
            vehicle = {'vehicle_id': sale_order.vehicle_id.id}
            res.update(vehicle)
        return res
