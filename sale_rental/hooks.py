# Copyright 2016-2019 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.api import Environment


def add_to_group_stock_packaging(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    conf_page = env['res.config.settings'].create({})
    conf_page.group_stock_packaging = True
    conf_page.execute()
