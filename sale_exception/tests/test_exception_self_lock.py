# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo import Command
from odoo.api import Environment
from odoo.sql_db import db_connect
from odoo.tests import TransactionCase

from odoo.addons.base_exception.exceptions import BaseExceptionError


class TestSaleExceptionSelfLock(TransactionCase):
    """Regression test: editing a confirmed sale order so that an exception
    rule matches must not hang forever.

    Exception flags are written through a genuinely independent DB
    connection (``registry.cursor()``) so they survive a rollback of the
    ongoing transaction. When that transaction already holds locks on the
    rows the independent connection has to write (e.g. an order line written
    and flushed earlier in the same transaction), the independent connection
    waits for the ongoing transaction, while the ongoing transaction waits in
    Python for the independent connection to finish. PostgreSQL cannot
    detect this as a deadlock, so the request (and the Odoo worker) hung
    until it was killed.

    During tests ``registry.cursor()`` returns a cursor sharing the test
    connection, which can never wait for itself. While saving the order it
    is replaced by genuinely separate connections, as outside tests. Those
    connections only see committed rows, so the confirmed order is created
    and committed through one of them, and removed at the end. A
    ``statement_timeout`` turns a regression into a failure instead of a
    hanging test run.
    """

    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, test_base_exception=True))
        self.real_cr = self._independent_cursor()
        self.addCleanup(self.real_cr.close)
        self.real_env = Environment(self.real_cr, self.env.uid, {})
        self.rule = self.real_env["exception.rule"].create(
            {
                "name": "Self lock test: sold below cost",
                "model": "sale.order.line",
                "exception_type": "by_py_code",
                "code": "failed = obj.price_unit < obj.product_id.standard_price",
            }
        )
        self.product = self.real_env["product.product"].create(
            {
                "name": "Self lock test product",
                "list_price": 20.0,
                "standard_price": 10.0,
            }
        )
        self.order = self.real_env["sale.order"].create(
            {
                "partner_id": self.real_env.ref("base.res_partner_1").id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        self.order.action_confirm()
        self.real_cr.commit()
        self.addCleanup(self._remove_committed_records)

    def _independent_cursor(self):
        cr = db_connect(self.env.cr.dbname).cursor()
        cr.execute("SET statement_timeout = 20000")
        return cr

    def _remove_committed_records(self):
        self.real_cr.rollback()
        self.order.with_env(self.real_env)._action_cancel()
        self.order.with_env(self.real_env).unlink()
        self.product.with_env(self.real_env).product_tmpl_id.unlink()
        self.rule.with_env(self.real_env).unlink()
        self.real_cr.commit()

    def test_edit_confirmed_order_does_not_self_lock(self):
        order = self.order.with_env(self.env)
        self.assertEqual(order.state, "sale")
        line = order.order_line
        # Rolling back this savepoint releases the locks taken by the edits
        # before the committed records are removed.
        savepoint = self.env.cr.savepoint()
        self.addCleanup(savepoint.close)
        with patch.object(
            self.registry, "cursor", side_effect=self._independent_cursor
        ):
            # Earlier work of the same transaction that reached the database
            # keeps the line locked (in production, sale_stock flushed the
            # edited lines when updating their stock moves).
            order.write(
                {"order_line": [Command.update(line.id, {"product_uom_qty": 2})]}
            )
            self.env.flush_all()
            # Sell that line below cost and save. assertRaises() rolls back the
            # changes made by the save, as the request does when the exception
            # is raised to the user.
            with self.assertRaises(BaseExceptionError):
                order.write(
                    {"order_line": [Command.update(line.id, {"price_unit": 5.0})]}
                )
        # The independent connection could not write the locked rows, so the
        # exceptions were written in the rolled back transaction...
        self.assertFalse(line.exception_ids)
        self.assertFalse(order.exception_ids)
        # ...and are written again, in a new committed transaction, once the
        # transaction has rolled back and released its locks.
        savepoint.close(rollback=True)
        with patch.object(
            self.registry, "cursor", side_effect=self._independent_cursor
        ):
            self.env.cr.postrollback.run()
        self.real_cr.rollback()
        self.assertEqual(line.with_env(self.real_env).exception_ids, self.rule)
        self.assertEqual(order.with_env(self.real_env).exception_ids, self.rule)
