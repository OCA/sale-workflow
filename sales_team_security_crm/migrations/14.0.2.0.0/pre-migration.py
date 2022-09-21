# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Adjust record rules according new definition."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    record = env.ref("sales_team_security_crm.crm_lead_team_rule", False)
    if record:
        record.domain_force = (
            "['|', '|', ('user_id','=',user.id), ('user_id','=',False), '|', "
            "('team_id', '=', user.sale_team_id.id), ('team_id', '=', False)]"
        )
    record = env.ref("sales_team_security_crm.crm_activity_report_team", False)
    if record:
        record.domain_force = (
            "['|', '|', ('user_id','=',user.id), ('user_id','=',False), '|', "
            "('team_id', '=', user.sale_team_id.id), ('team_id', '=', False)]"
        )
