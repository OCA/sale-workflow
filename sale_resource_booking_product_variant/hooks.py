from openupgradelib import openupgrade


def post_init_hook(cr, registry):
    sql = """
        UPDATE product_product p
        SET
            resource_booking_type_id = t.resource_booking_type_id,
            resource_booking_type_combination_rel_id =
                t.resource_booking_type_combination_rel_id
        FROM product_template as t
        WHERE p.product_tmpl_id = t.id;
    """
    openupgrade.logged_query(cr, sql)


def uninstall_hook(cr, registry):
    sql = """
        UPDATE product_template t
        SET
            resource_booking_type_id = p.resource_booking_type_id,
            resource_booking_type_combination_rel_id =
                p.resource_booking_type_combination_rel_id
        FROM (
            SELECT
                product_tmpl_id,
                CASE WHEN COUNT(*)=1
                     THEN AVG(resource_booking_type_id)::INTEGER
                     ELSE NULL END AS resource_booking_type_id,
                CASE WHEN COUNT(*)=1
                     THEN AVG(resource_booking_type_combination_rel_id)::INTEGER
                     ELSE NULL END AS resource_booking_type_combination_rel_id
            FROM (
                SELECT product_tmpl_id, resource_booking_type_id,
                    resource_booking_type_combination_rel_id
                FROM product_product
                GROUP BY product_tmpl_id, resource_booking_type_id,
                    resource_booking_type_combination_rel_id
            ) AS tmpl_and_type_and_combination_rel
            GROUP BY product_tmpl_id
        ) AS p
        WHERE p.product_tmpl_id = t.id;
    """
    openupgrade.logged_query(cr, sql)
