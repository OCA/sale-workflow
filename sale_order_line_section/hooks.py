# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Initialize stored value for section_id before module installation."""
    cr = env.cr
    if column_exists(cr, "sale_order_line", "section_id"):
        return

    _logger.info("Create and initialize sale_order_line.section_id")
    create_column(cr, "sale_order_line", "section_id", "INTEGER")
    cr.execute(
        """
        WITH ordered_lines AS (
            SELECT
                sol.id,
                sol.display_type,
                MAX(CASE WHEN sol.display_type = 'line_section' THEN sol.id END)
                    OVER (
                        PARTITION BY sol.order_id
                        ORDER BY sol.sequence, sol.id
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                    ) AS previous_section_id
            FROM sale_order_line sol
        )
        UPDATE sale_order_line sol
        SET section_id = CASE
            WHEN ol.display_type = 'line_section' THEN NULL
            ELSE ol.previous_section_id
        END
        FROM ordered_lines ol
        WHERE sol.id = ol.id
        """
    )
