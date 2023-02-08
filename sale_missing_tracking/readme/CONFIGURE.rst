To configure pricelists with the new feature of this module, you need to:

#. Go to *Sales > Configuration > Settings > Missing products tracking*.
#. Set options to adjust amounts and periods.


OPTIONAL:

If you want to set a grace period between one notice and the next,
you can follow these steps:

#. Activate developer mode.
#. Go to *Settings > Technical > Parameters > System Parameters*.
#. Create a new setting with key
   "sale_missing_tracking.already_notified_relativedelta_params".
   Fill value with a dictionary with params used in dateutil.relativedelta Class.

 Examples:

 * To receive only one notification per calendar week in GMT+1:
    | {"weeks": -1, "weekday": 6, "hour": 22, "minute": 59, "second": 59,
      "microsecond": 99999}
