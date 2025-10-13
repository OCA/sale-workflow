from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Convert route_id Many2one field to route_ids Many2many field."""
    openupgrade.m2o_to_x2m(
        env.cr,
        env["sale.order.type"],
        "sale_order_type",
        "route_ids",
        "route_id",
    )
