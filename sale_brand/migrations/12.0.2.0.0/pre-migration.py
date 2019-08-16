# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Move sale brand to res.brand model")
    cr.execute(
        """ALTER TABLE sale_order
        ADD COLUMN brand_id_tmp INTEGER"""
    )
    cr.execute("""UPDATE sale_order  SET brand_id_tmp = brand_id""")
    cr.execute("""ALTER TABLE sale_order DROP COLUMN brand_id""")
