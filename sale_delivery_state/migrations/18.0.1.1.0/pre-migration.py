# Copyright 2025 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale_delivery_state.hooks import _setup_new_columns


def migrate(cr, version):
    _setup_new_columns(cr)
