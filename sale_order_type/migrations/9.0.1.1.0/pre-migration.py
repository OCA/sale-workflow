# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, SUPERUSER_ID
from datetime import datetime


def migrate_sale_journal(cr):
    """Check if this comes from renaming the module `sale_journal`, and
    if so, it processes data for adapting to the new layout.
    """
    cr.execute(
        'SELECT 1 FROM pg_class WHERE relname = %s',
        ('sale_journal_invoice_type', ),
    )
    if not cr.fetchone():
        return
    from openupgradelib import openupgrade
    env = api.Environment(cr, SUPERUSER_ID, {})
    openupgrade.rename_tables(
        cr, [('sale_journal_invoice_type', 'sale_order_type')],
    )
    openupgrade.rename_models(
        cr, [('sale_journal.invoice.type', 'sale.order.type')],
    )
    openupgrade.rename_property(
        cr, 'res.partner', 'property_invoice_type', 'sale_type',
    )
    openupgrade.rename_fields(
        env, [
            ('res.partner', 'res_partner', 'property_invoice_type',
             'sale_type'),
            ('sale.order', 'sale_order', 'invoice_type_id', 'type_id'),
            ('sale.order.type', 'sale_order_type', 'note', 'description'),
        ],
    )
    cr.execute(
        "ALTER TABLE sale_order_type ALTER invoicing_method DROP NOT NULL",
    )


def migrate_to_property(cr):
    """Check if this comes from the previous revision inside same Odoo version
    verifying if a column exists. If so, then the column values are converted
    to property values.
    """
    cr.execute(
        """SELECT count(attname) FROM pg_attribute
        WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = %s)
        AND attname = %s""", ('res_partner', 'sale_type'),
    )
    if cr.fetchone()[0] == 0:
        return
    cr.execute(
        "SELECT id, sale_type FROM res_partner WHERE sale_type IS NOT NULL")
    partners = cr.fetchall()
    cr.execute(
        "SELECT f.id "
        "FROM ir_model_fields f "
        "JOIN ir_model m ON m.id = f.model_id "
        "WHERE m.model = 'res.partner' AND f.name = 'sale_type'")
    type_fields = cr.fetchall()
    if len(type_fields) != 1:
        raise Exception("Can't find 1 'sale_type' field")
    cr.execute(
        "SELECT id FROM res_company")
    companies = cr.fetchall()
    for partner in partners:
        for company in companies:
            utcnow = str(datetime.utcnow())
            cr.execute(
                "INSERT INTO ir_property("
                "create_date, create_uid, write_date, name, company_id, type, "
                "fields_id, res_id, value_reference) "
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
                % (
                    utcnow, SUPERUSER_ID, utcnow, 'sale_type', company[0],
                    'many2one', type_fields[0][0],
                    'res.partner,%s' % partner[0],
                    'sale.order.type,%s' % partner[1]
                )
            )


def migrate(cr, version):
    if not version:
        return
    migrate_to_property(cr)
    migrate_sale_journal(cr)
