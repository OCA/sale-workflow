# Copyright 2023 Sylvain LE GAL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info(
        "sale.order.line: Create 'weight', 'total_ordered_weight' and"
        " 'total_delivered_weight' to be fast initialized."
    )
    cr.execute(
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS unit_weight NUMERIC,
        ADD COLUMN IF NOT EXISTS total_ordered_weight DOUBLE PRECISION,
        ADD COLUMN IF NOT EXISTS total_delivered_weight DOUBLE PRECISION;
        """)
    _logger.info(
        "sale.order.line model :"
        " Initialize 'unit weight';"
        " precompute 'total_ordered_weight' and 'total_delivered_weight'"
    )
    cr.execute("""
        UPDATE sale_order_line
        SET unit_weight = product_product.weight,
            total_ordered_weight = product_product.weight * product_uom_qty,
            total_delivered_weight = product_product.weight * qty_delivered
        FROM product_product
        WHERE product_product.id = sale_order_line.product_id
        AND product_product.weight != 0;
        """)

    _logger.info(
        "sale.order: Create 'total_ordered_weight' and"
        " 'total_delivered_weight' to be fast initialized."
    )
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS total_ordered_weight DOUBLE PRECISION,
        ADD COLUMN IF NOT EXISTS total_delivered_weight DOUBLE PRECISION;
        """)

    _logger.info(
        "sale.order model :"
        " precompute 'total_ordered_weight' and 'total_delivered_weight'"
    )
    cr.execute(
        """
        UPDATE sale_order
        SET total_ordered_weight = tmp.total_ordered_weight,
            total_delivered_weight = tmp.total_delivered_weight
        FROM (
            SELECT order_id,
            sum(total_ordered_weight) as total_ordered_weight,
            sum(total_delivered_weight) as total_delivered_weight
            FROM sale_order_line group by order_id
        ) as tmp
        WHERE tmp.order_id = sale_order.id
        AND (tmp.total_ordered_weight != 0.0
            OR tmp.total_delivered_weight != 0.0);
        """)
