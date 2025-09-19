# Copyright 2025 Raumschmiede GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools.sql import column_exists, create_column


def migrate(cr, version):
    if column_exists(cr, "sale_order_line", "main_exception_id"):
        return

    create_column(cr, "sale_order_line", "main_exception_id", "int4")
