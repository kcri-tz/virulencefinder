# Slimmed down VirulenceFinder repository

This repository is a slimmed down copy of the upstream repository at
<https://bitbucket.org/genomicepidemiology/virulencefinder>.  It exists to
enable rapid download of this CGE service.

The code in this repository is periodically updated from the upstream repo,
and version tags mirror the upstream tags, with a fourth decimal added to
indicate the exact commit that was copied over:

    $ git describe (upstream)  →  $ git describe (here)
    3.0.2-6-g6dfe              →  3.0.2.6  (6th commit after 3.0.2)

Note that test data and other extraneous upstream files are omitted
from this repository.

Though this repository will trail behind the latest upstream development,
it is kept in sync with the requirements of the latest version of the
[KCRI CGE Bacterial Analysis Pipeline](https://github.com/kcri-tz/kcri-cge-bap).

#### Rationale

The reason for maintaining this repository (and the other slimmed down
repos at <https://github.com/kcri-tz/>) is that several CGE services, due
to spurious binary commits in the past, have huge git histories.

Cloning the standard services for the BAP adds up to a whopping 1.6GB
download, whereas the actual source code is less than 1MB.  We will drop
this repo once the issue has been fixed upstream.

