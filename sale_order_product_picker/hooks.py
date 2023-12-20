# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def _post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ICP = env["ir.config_parameter"]
    previous_value = ICP.get_param("sale_planner_calendar.action_open_sale_order")
    if previous_value:
        ICP.set_param(
            "sale_planner_calendar.action_open_sale_order_bak", previous_value
        )
    ICP.set_param(
        "sale_planner_calendar.action_open_sale_order",
        "sale_order_product_picker.action_open_picker_views",
    )


def _uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ICP = env["ir.config_parameter"]
    previous_value = ICP.get_param("sale_planner_calendar.action_open_sale_order_bak")
    if previous_value:
        ICP.set_param("sale_planner_calendar.action_open_sale_order", previous_value)
    else:
        ICP.search(
            [
                ("key", "=", "sale_planner_calendar.action_open_sale_order"),
                ("value", "=", "sale_order_product_picker.action_open_picker_views"),
            ]
        ).unlink()
