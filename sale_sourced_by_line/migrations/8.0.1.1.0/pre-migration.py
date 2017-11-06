# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


column_renames = {
    'sale_order_line': [
        ('location_id', None),
    ]
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
