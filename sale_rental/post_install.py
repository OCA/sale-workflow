# -*- coding: utf-8 -*-
# © 2016-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def add_users_to_group_mrp_properties(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        users = env['res.users'].search(
            ['|', ('active', '=', True), ('active', '=', False)])
        users.write({
            'groups_id': [(4, env.ref('sale.group_mrp_properties').id)]})
    return
