This module allows to delete Quotations and related partner records when those are older than a definable retention period.

Features:

* Configure a retention period of x hours (default: 48 hours)

* Specify a maximum of abandoned items to be deleted at a time (default: 2000 items) in order to avoid unresponsive server

* A log for reviewing purposes

Algorithm
=========

This module identifies orders as abandoned (and to be deleted) if all of the following is true:

`"state = draft" and "sales = website_sales" and "date_of_order <= hours_from_retention_period"`

These orders will be displayed in "Abandoned orders" and can be deleted manually. 

Customers, which have

`"orders = 0" and "lead = 0" and "meetings = 0" and "opportunities = 0" and "calls = 0" and "invoice = 0" and "tasks = 0" and "active = 0" and "is_customer = true"`

will be displayed in "Abandoned customers" and can be deleted manually.

A cron job can be configured to delete abandoned orders and abandoned customers automatically.

Deleted items are listed with name, date, model & user in "Removed Log" for verification purposes.

Configuration
=============

Under Settings -> Configuration -> Sales -> Retention Period set hours and maximum abandoned items:

.. image:: images/1_settings.png

**How to set automation (cron job) to delete orders?**

Go to settings -> Activate the developer mode, Technical: Automation -> Scheduled Actions.

Type in Name, Interval Number, Next Execution Date and Inverval Unit. The cron job will be executed at Next Execution Date. In Number of calls you can determine how many intervals it has to run. 

For example:

"Number of calls = 1", "Interval Unit = Days" and "next Execution Date = 12/16/2019 15:45:44" means: It runs only one day beginning with this date.

"Number of calls = 7", "Interval Unit = Days" and "next Execution Date = 12/16/2019 15:45:44" means: It runs seven days beginning with this date.

"Number of calls is negative" means that this process will run every day. 

.. image:: images/2_cron_job.png


Usage
=====

**How to find removable orders with draft-status?**

Go to Sales -> Abandoned Log: Abandoned Order. When you click on the "bin" Symbol on the right side, you can skip the order from the removing-process. If you scroll down and click on the red remove button, all listed orders will be deleted.

.. image:: images/3_abandoned_order.png

**How to see which data was deleted?**

Go to Sales -> Abandoned Log: Removed Log

.. image:: images/4_removed_log.png

You can export the data to a CSV file if you activate the check box on the left side and go to more -> export.

.. image:: images/5_export.png

**How to view and delete customers with zero orders?**

After deleting abandoned orders, customers will not be removed automatically. In order to do so go to Sales -> Abandoned Log: Abandoned Customer. When you click on the "bin" Symbol on the right side, you can skip the customer from the removing process. If you scroll down and click on the red remove button, all listed customers will be deleted.

.. image:: images/6_abandoned_customer.png
