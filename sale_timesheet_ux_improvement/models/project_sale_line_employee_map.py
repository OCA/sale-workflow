# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProductEmployeeMap(models.Model):
    _inherit = 'project.sale.line.employee.map'

    currency_id = fields.Many2one(related='sale_line_id.currency_id')
