# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging


def pre_init_hook(cr):
    """ Precreate is_fully_delivered and invoice_status_validated and
    fill with appropriate values to prevent
    long time waiting for the computation when installing this """
    logger = logging.getLogger(__name__)
    logger.info("Add sale_order.is_fully_delivered column if it does not yet exist")
    cr.execute(
        "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS is_fully_delivered BOOLEAN"
    )
    logger.info(
        "Add sale_order.invoice_status_validated column if it does not yet exist"
    )
    cr.execute(
        "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS invoice_status_validated VARCHAR"
    )

    cr.execute(
        """
    UPDATE sale_order
    SET invoice_status_validated =
    (CASE
        WHEN (SELECT COUNT(*)
                FROM sale_order_line
                WHERE order_id = sale_order.id
                AND qty_invoiced >= product_uom_qty
                AND NOT is_delivery) = (SELECT COUNT(*)
            FROM sale_order_line
                WHERE order_id = sale_order.id AND NOT is_delivery) THEN 'invoiced'
        ELSE 'no'
    END)
    """
    )
    cr.execute(
        """UPDATE sale_order
    SET invoice_status_validated = 'to invoice' WHERE invoice_status = 'to invoice';"""
    )
    cr.execute(
        """UPDATE sale_order SET invoice_status_validated = 'invoiced'
    WHERE invoice_status = 'invoiced';"""
    )
    logger.info("Filling invoice_status_validated column")

    cr.execute(
        """
UPDATE sale_order
SET is_fully_delivered =
    (CASE
        WHEN (SELECT COUNT(*)
              FROM sale_order_line
              WHERE order_id = sale_order.id
                AND qty_delivered >= product_uom_qty
                 AND NOT is_delivery) = (SELECT COUNT(*)
                 FROM sale_order_line
                 WHERE order_id = sale_order.id AND NOT is_delivery) THEN true
        ELSE false
    END);

"""
    )
    logger.info("Filling is_fully_delivered column")
