This module allows to execute workflows with a different frequence than
the related module.
This is achieved by having an other cron job independent to the first one.

In the workflow configuration, an option can be set to run with delay.
In such case that option will be executed by the delayed cron job and not
the regular one.

At the moment only the sales order validation option can be set this way.
