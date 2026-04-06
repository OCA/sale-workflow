# Copyright 2023 Sylvain LE GAL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info(
        "sale.order.line: Create 'total_ordered_weight' and"
        " 'total_delivered_weight' to be fast initialized."
    )
    cr.execute(
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS total_ordered_weight DOUBLE PRECISION,
        ADD COLUMN IF NOT EXISTS total_delivered_weight DOUBLE PRECISION;
        """
    )
    _logger.info(
        "sale.order.line model :"
        " precompute 'total_ordered_weight' and 'total_delivered_weight'"
    )
    cr.execute(
        """
        UPDATE sale_order_line
        SET
            total_ordered_weight = (
                product.weight
                * sale_order_line.product_uom_qty
                / line_uom.factor
                * template_uom.factor
            ),
            total_delivered_weight = (
                product.weight
                * sale_order_line.qty_delivered
                / line_uom.factor
                * template_uom.factor
            )
        FROM
            product_product product,
            product_template template,
            uom_uom as template_uom,
            uom_uom as line_uom
        WHERE product.id = sale_order_line.product_id
        AND template.id = product.product_tmpl_id
        AND template.uom_id = template_uom.id
        AND sale_order_line.product_uom = line_uom.id
        AND product.weight != 0;
        """
    )

    _logger.info(
        "sale.order: Create 'total_ordered_weight' and"
        " 'total_delivered_weight' to be fast initialized."
    )
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS total_ordered_weight DOUBLE PRECISION,
        ADD COLUMN IF NOT EXISTS total_delivered_weight DOUBLE PRECISION;
        """
    )

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
        """
    )
