# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tools import SQL


def _fill_in_related_sale_line_sql(env):
    """
    Update all the chained moves with the related sale line
    """
    query = SQL(
        """
            WITH RECURSIVE linked_moves AS (
                SELECT
                    id AS move_id,
                    sale_line_id AS root_sale_line_id
                FROM
                    stock_move
                WHERE
                    sale_line_id IS NOT NULL

                UNION
                SELECT
                    smr.move_orig_id AS move_id,
                    lm.root_sale_line_id
                FROM
                    stock_move_move_rel smr
                INNER JOIN
                    linked_moves lm ON smr.move_dest_id = lm.move_id
            )
            UPDATE
                stock_move sm
            SET
                related_sale_line_id = lm.root_sale_line_id
            FROM
                linked_moves lm
            WHERE
                sm.id = lm.move_id
                ;
        """
    )
    env.cr.execute(query)


def post_init_hook(env):
    _fill_in_related_sale_line_sql(env)
