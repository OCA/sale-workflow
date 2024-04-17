# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tools import sql


def migrate(cr, version):
    if sql.column_exists(cr, "res_company", "carrier_auto_assign"):
        sql.rename_column(
            cr, "res_company", "carrier_auto_assign", "carrier_auto_assign_on_confirm"
        )
