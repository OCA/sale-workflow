import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Create column order_type in sale_order with default value 'order'")
    cr.execute(
        "ALTER TABLE sale_order ADD COLUMN order_type varchar(255) DEFAULT 'order'"
    )
    # drop the default value since it was only used to fill the column in existing records
    cr.execute("ALTER TABLE sale_order ALTER COLUMN order_type DROP DEFAULT")

    _logger.info(
        "Create column order_type in sale_order_line with default value 'order'"
    )
    cr.execute(
        "ALTER TABLE sale_order_line ADD COLUMN order_type varchar(255) DEFAULT 'order'"
    )
    # drop the default value since it was only used to fill the column in existing records
    cr.execute("ALTER TABLE sale_order_line ALTER COLUMN order_type DROP DEFAULT")

    _logger.info(
        "Create columns for blanket order in sale_order and "
        "sale_order_line to avoid computing the field for all records at module install"
    )
    # avoid computing the field for all records at module install
    cr.execute(
        "ALTER TABLE sale_order_line ADD COLUMN call_off_remaining_qty double precision"
    )
    cr.execute(
        "ALTER TABLE sale_order_line ADD COLUMN blanket_validity_start_date date"
    )
    cr.execute("ALTER TABLE sale_order_line ADD COLUMN blanket_validity_end_date date")
    cr.execute("ALTER TABLE sale_order_line ADD COLUMN blanket_order_id integer")
    cr.execute(
        "ALTER TABLE sale_order ADD COLUMN blanket_reservation_strategy varchar(255)"
    )

    cr.execute(
        "ALTER TABLE sale_order ADD COLUMN create_call_off_from_so_if_possible BOOLEAN"
    )
