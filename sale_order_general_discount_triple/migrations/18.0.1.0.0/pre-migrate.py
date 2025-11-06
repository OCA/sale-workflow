from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    config_parameter = env["ir.config_parameter"].search(
        [
            (
                "key",
                "in",
                [
                    "sale_order_general_discount_triple.general_discount",
                    "sale_order_general_discount_triple.pricelist_discount",
                ],
            ),
            ("value", "=", "discount"),
        ]
    )
    if config_parameter:
        config_parameter.sudo().write({"value": "discount1"})
