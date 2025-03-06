# Copyright 2018-2016 Tecnativa - Pedro M. Baeza
# Copyright 2020 - Iván Todorovich
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def post_init_hook(env):
    # At installation time, we need to sync followers
    partners = env["res.partner"].search(
        [
            ("parent_id", "=", False),
            ("is_company", "=", True),
            "|",
            ("user_id", "!=", False),
            ("child_ids.user_id", "!=", False),
        ]
    )
    partners._add_followers_from_salesmen()


def uninstall_hook(env):  # pragma: no cover
    """At uninstall, revert changes made to record rules"""
    env.ref("sales_team.group_sale_salesman_all_leads").write(
        {
            "implied_ids": [
                (6, 0, [env.ref("sales_team.group_sale_salesman").id]),
            ],
        }
    )
