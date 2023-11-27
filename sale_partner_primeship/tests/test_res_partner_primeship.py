# Copyright 2024 Akretion - Olivier Nibart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from .common import TestCommon


class TestResPartnerPrimeship(TestCommon):
    def test_compute_active_primeship(self):
        active_primeship = self.make_primeship(
            date.today() - timedelta(days=1), date.today() + timedelta(days=30)
        )
        self.assertTrue(active_primeship.current)
        self.partner._compute_active_primeship()
        self.assertTrue(self.partner.active_primeship)

        expired_primeship = self.make_primeship(
            date.today() - timedelta(days=60), date.today() - timedelta(days=30)
        )
        self.assertFalse(expired_primeship.current)
        self.partner._compute_active_primeship()
        # Still true due to active primeship
        self.assertTrue(self.partner.active_primeship)

        active_primeship.active = False
        self.partner._compute_active_primeship()
        self.assertFalse(self.partner.active_primeship)

    def test_compute_primeship_count(self):
        self.assertEqual(self.partner.primeship_count, 0)

        self.make_primeship(date.today(), date.today() + timedelta(days=30))
        self.partner._compute_primeship_count()
        self.assertEqual(self.partner.primeship_count, 1)

        self.make_primeship(
            date.today() + timedelta(days=31), date.today() + timedelta(days=60)
        )
        self.partner._compute_primeship_count()
        self.assertEqual(self.partner.primeship_count, 2)

    def test_check_expired_primeships(self):
        primeship = self.make_primeship(
            date.today() - timedelta(days=1), date.today() + timedelta(days=30)
        )
        self.assertTrue(self.partner.active_primeship)
        self.Partner._check_expired_primeships()
        self.assertTrue(self.partner.active_primeship)

        primeship.start_date = date.today() + timedelta(days=1)
        self.assertFalse(self.partner.active_primeship)
        self.partner.active_primeship = True
        self.Partner._check_expired_primeships()
        self.assertFalse(self.partner.active_primeship)

        # work also on inactive partners
        self.partner.active = False
        self.partner.active_primeship = True
        self.Partner._check_expired_primeships()
        self.assertFalse(self.partner.active_primeship)
