# Copyright 2026 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Enable the option on every company of an upgraded database, so it
    keeps splitting deliveries by date. New installations leave it off."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.company"].search([]).write({"sale_delivery_split_date": True})
