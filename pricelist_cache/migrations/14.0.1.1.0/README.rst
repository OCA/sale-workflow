We add a few new fields in this new version.
Those fields are meant to determine if cached prices can be retrieved or not.
The thing is, we cannot set it to True by default,
because pricelist cache jobs could be running or waiting at the moment of this migration.

During the pre script, the jobs which aren't STARTED, DONE, CANCELLED or FAILED are locked.
During the post script, those jobs are cancelled, and the pricelist cache will be created again.
