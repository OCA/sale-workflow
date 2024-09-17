# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

_logger = logging.getLogger(__name__)


def drop_base_automation_record(cr):
    query = """
        DELETE FROM base_automation
        WHERE id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE name = 'automation_update_product_pricelist_cache'
            AND module = 'pricelist_cache'
        )
        RETURNING id;
    """
    cr.execute(query)
    deleted_ids = [row[0] for row in cr.fetchall()]
    _logger.info(f"Deleted base_automation record with id {deleted_ids}")


def migrate(cr, version):
    drop_base_automation_record(cr)
