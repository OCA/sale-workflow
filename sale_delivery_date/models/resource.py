# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def write(self, vals):
        res = super().write(vals)
        # Clear cache to ensure 'ormcache' decorated methods on 'sale.order.line'
        # returns the expected results if calendar is updated
        self.clear_caches()
        return res


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        res = super().create(vals_list)
        # Clear cache to ensure 'ormcache' decorated methods on 'sale.order.line'
        # returns the expected results if attendances are created
        self.clear_caches()
        return res

    def write(self, vals):
        res = super().write(vals)
        # Clear cache to ensure 'ormcache' decorated methods on 'sale.order.line'
        # returns the expected results if attendances are updated
        self.clear_caches()
        return res


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        res = super().create(vals_list)
        # Clear cache to ensure 'ormcache' decorated methods on 'sale.order.line'
        # returns the expected results if leaves are created
        self.clear_caches()
        return res

    def write(self, vals):
        res = super().write(vals)
        # Clear cache to ensure 'ormcache' decorated methods on 'sale.order.line'
        # returns the expected results if leaves are updated
        self.clear_caches()
        return res
