from openupgradelib import openupgrade

xmlids_to_rename = [
    (
        "resource_booking_sale.resource_booking_type_form",
        "resource_booking_sale.resource_booking_type_view_form",
    ),
    (
        "resource_booking_sale.resource_booking_form",
        "resource_booking_sale.resource_booking_view_form",
    ),
]


def connect_resource_booking_type_with_product_variant(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE product_product
        ADD COLUMN resource_booking_type_id int4,
        ADD COLUMN resource_booking_type_combination_rel_id int4;
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_product p
        SET
            resource_booking_type_id = t.resource_booking_type_id,
            resource_booking_type_combination_rel_id =
                t.resource_booking_type_combination_rel_id
        FROM product_template as t
        WHERE p.product_tmpl_id = t.id
        AND (t.resource_booking_type_id > 0
            OR
            t.resource_booking_type_combination_rel_id > 0
        );
        """,
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):

    openupgrade.rename_xmlids(cr, xmlids_to_rename)

    connect_resource_booking_type_with_product_variant(cr)
