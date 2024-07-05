# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.mail.tests.common import MailCase


class TestSendMassMailQuotation(TransactionCase, MailCase):
    def setUp(self):
        super().setUp()

    def test_1(self):
        pass
