# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_view_sale_order_line = fields.Boolean(
        string="Enable Smart Button to view SO line right on SO Form",
        config_parameter="sale_order_line_input.show_view_sale_order_line ",
    )

    def set_values(self):
        res = super().set_values()
        group = self.env.ref("sale_order_line_input.sale_orderline_view_group")
        if self.show_view_sale_order_line:
            users = self.env["res.users"].search(
                [
                    (
                        "groups_id",
                        "in",
                        self.env.ref("sales_team.group_sale_salesman").id,
                    )
                ]
            )
            users.write({"groups_id": [(4, group.id)]})
        else:
            users = self.env["res.users"].search([("groups_id", "in", [group.id])])
            users.write({"groups_id": [(3, group.id)]})
        return res
