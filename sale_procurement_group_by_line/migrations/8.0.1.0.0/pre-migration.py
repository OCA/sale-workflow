# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def find_procurements(env):
    groups = env['sale.order.line.group'].search([])
    for group in groups:
        procurements = env['procurement.order'].search(
            [('sale_line_id', '=', group.sale_line_id)])
        if procurements:
            proc_group = env['procurement.group'].create({
                             'name': group.name
            })
            procurements.write({'group_id': proc_group.id})


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    find_procurements(env)
