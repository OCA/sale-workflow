# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def assign_warehouse(env):
    sales = env['sale.order'].search([])
    for so in sales:
        so.order_line.write({'warehouse_id': so.warehouse_id.id})


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    assign_warehouse(env)
