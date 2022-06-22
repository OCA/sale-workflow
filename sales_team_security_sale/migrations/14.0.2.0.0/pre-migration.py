# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Adjust record rules according new definition."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    record = env.ref("sales_team_security_sale.sale_order_team_rule", False)
    if record:
        record.domain_force = (
            "['|', '|', ('user_id','=',user.id), ('user_id','=',False), '|', "
            "('team_id', '=', user.sale_team_id.id), ('team_id', '=', False)]"
        )
    record = env.ref("sales_team_security_sale.sale_order_report_team_rule", False)
    if record:
        record.domain_force = (
            "['|', '|', ('user_id','=',user.id), ('user_id','=',False), '|', "
            "('team_id', '=', user.sale_team_id.id), ('team_id', '=', False)]"
        )
    record = env.ref("sales_team_security_sale.sale_order_line_team_rule", False)
    if record:
        record.domain_force = (
            "['|', '|', ('salesman_id','=',user.id), ('salesman_id','=',False), '|', "
            "('order_id.team_id', '=', user.sale_team_id.id), "
            "('order_id.team_id', '=', False)]"
        )
