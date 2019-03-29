In a sale order line (form view, not tree view), if you select a rental service, you can :

* create a new rental with a start date and an end date: when the sale order is confirmed, it will generate a delivery order and an incoming shipment.
* extend an existing rental: the incoming shipment will be postponed to the end date of the extension.

In a sale order line, if you select a product that has a corresponding rental service, you can decide to sell the rented product that the customer already has. If the sale order is confirmed, the incoming shipment will be cancelled and a new delivery order will be created with a stock move from *Rental Out* to *Customers*.

Please refer to this screencast https://www.youtube.com/watch?v=9o0QrGryBn8 to get a demo of the installation, configuration and use of this module (note that this screencast is for Odoo v7).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/11.0
