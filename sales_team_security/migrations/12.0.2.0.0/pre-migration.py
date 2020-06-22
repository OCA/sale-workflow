# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """Remove obsolete record rules."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    xmlids = [
        "res_partner_team_rule",
        "res_partner_personal_rule",
        "res_partner_manager_rule",
    ]
    for xmlid in xmlids:
        rec = env.ref("sales_team_security." + xmlid, False)
        if rec:
            rec.unlink()
