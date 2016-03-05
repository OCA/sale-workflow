# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    section_ids = fields.Many2many(
        comodel_name="crm.case.section", string="Sales teams",
        relation='sale_member_rel', column1='member_id', column2='section_id')
