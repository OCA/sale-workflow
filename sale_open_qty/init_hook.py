# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging


logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.
    """
    store_field_qty_to_deliver(cr)


def store_field_qty_to_deliver(cr):

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='sale_order_line' AND
    column_name='qty_to_deliver'""")
    if not cr.fetchone():
        logger.info('Creating field qty_to_deliver on sale_order_line')
        cr.execute(
            """
            ALTER TABLE sale_order_line ADD COLUMN qty_to_deliver float;
            COMMENT ON COLUMN sale_order_line.qty_to_deliver IS
            'To Deliver';
            """)

    logger.info('Computing values for field qty_to_deliver'
                ' on sale_order_line')
    cr.execute(
        """
        UPDATE sale_order_line sol
        SET qty_to_deliver = sol.product_uom_qty - sol.qty_delivered
        """
    )
