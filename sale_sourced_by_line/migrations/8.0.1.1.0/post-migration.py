# -*- coding: utf-8 -*-
# Copyright 2017 Eficent - Miquel Raich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def populate_order_line_location_id(env):
    env.cr.execute(
        """
        SELECT %s
        FROM sale_order_line
        GROUP BY %s
        """ % (openupgrade.get_legacy_name('location_id'),
               openupgrade.get_legacy_name('location_id'))
    )
    locations = env.cr.fetchall()
    for location in locations:
        location_id = env['stock.location'].browse(location[0])
        wh = env['stock.location'].get_warehouse(env.cr, env.uid, location_id)
        env.cr.execute(
            """
            UPDATE sale_order_line
            SET warehouse_id = %s
            WHERE warehouse_id is NULL and %s = %s
            """ % (wh.id, openupgrade.get_legacy_name('location_id'),
                   location[0])
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    populate_order_line_location_id(env)
