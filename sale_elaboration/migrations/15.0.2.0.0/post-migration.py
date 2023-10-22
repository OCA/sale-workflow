# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.m2o_to_x2m(
        env.cr,
        env["sale.order.line"],
        "sale_order_line",
        "elaboration_ids",
        openupgrade.get_legacy_name("elaboration_id"),
    )
    # Update ir.exports.line name
    model_obj = env["ir.model"]
    fields_obj = env["ir.model.fields"]
    for line in env["ir.exports.line"].search([]):
        model = model_obj.search([("model", "=", line.export_id.resource)])
        field_name_list = line.name.split("/")
        updated = False
        for index in range(len(field_name_list)):
            field_name = field_name_list[index]
            field = fields_obj.search(
                [("name", "=", field_name), ("model_id", "=", model.id)]
            )
            if (
                field_name == "elaboration_id"
                and field.relation == "product.elaboration"
            ):
                field_name_list[index] = "elaboration_ids"
                updated = True
                break
            model = model_obj.search([("model", "=", field.relation)])
        if updated:
            line.name = "/".join(field_name_list)
