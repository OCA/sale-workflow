# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def _fill_sale_order_type(cr):
    _logger.info("Fill type_id in sale order if null as it is now required")

    cr.execute(
        """
    UPDATE sale_order
    SET
        type_id=(SELECT id FROM sale_order_type ORDER BY id LIMIT 1)
    WHERE
        type_id is null
        """
    )


def migrate(cr, version):
    _fill_sale_order_type(cr)
