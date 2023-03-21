# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    # Copy elaborations from sale order lines to stock moves
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO product_elaboration_stock_move_rel
            (stock_move_id, product_elaboration_id)
        SELECT sm.id AS stock_move_id,
               pesol.product_elaboration_id AS product_elaboration_id
        FROM stock_move sm
            LEFT JOIN product_elaboration_sale_order_line_rel pesol
                ON pesol.sale_order_line_id = sm.sale_line_id
        WHERE sm.sale_line_id is not null AND pesol.product_elaboration_id is not null
        """,
    )
