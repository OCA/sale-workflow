# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api

_logger = logging.getLogger(__name__)


def _remove_extra_sequence(cr):
    cr.execute(
        """
        select id from ir_sequence
        where id > (
            select min(id) from ir_sequence
            where code='sale.quotation'
            group by code, company_id having count(*) > 1
        );
    """
    )
    ids = [rec["id"] for rec in cr.dictfetchall()]
    if not ids:
        return
    _logger.info("Remove unnecessary sale.quotation ir_sequence " + str(ids))
    env = api.Environment(cr, 1, {})
    seqs = env["ir.sequence"].browse(ids)
    seqs.unlink()


def migrate(cr, version):
    _remove_extra_sequence(cr)
