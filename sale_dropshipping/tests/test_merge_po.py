from mock import Mock

from openerp.tests.common import BaseCase
from openerp.osv.orm import browse_record


class TestGroupOrders(BaseCase):

    def setUp(self):
        super(TestGroupOrders, self).setUp()
        self.order1 = Mock()
        self.order2 = Mock()
        # I have to use the registry to get an instance of a model. I cannot
        # use the class constructor because that is modified to return nothing.
        self.po = self.registry('purchase.order')

    def test_two_orders_different_destination_addresses(self):
        """Orders with the same partner, location, pricelist, but different
        destination addresses should not be merged.

        We do not care about the order lines here.
        """
        self.order1.partner_id = self.order2.partner_id = Mock(
            spec=browse_record, id=1)
        self.order1.location_id = self.order2.location_id = Mock(
            spec=browse_record, id=2)
        self.order1.pricelist_id = self.order2.pricelist_id = Mock(
            spec=browse_record, id=3)
        self.order1.order_line = self.order2.order_line = []

        self.order1.dest_address_id = Mock(spec=browse_record, id=5)
        self.order2.dest_address_id = Mock(spec=browse_record, id=6)

        grouped = self.po._group_orders([self.order1, self.order2])
        self.assertEqual(grouped, {}, u'These orders should not be merged')
