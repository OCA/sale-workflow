import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Updating states for sale_blanket_order " + str(version))
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_blanket_order sbo
        SET state = 'cancel'
        WHERE sbo.state = 'expired'
        """,
    )
    env.cr.commit()
