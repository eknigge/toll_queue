# Introduction
The purpose of this module is to import historical transactional data and simulate traffic queues. Users can  customize a facility so that a variety of lanes and configurations can be explored and tested before a final result is selected. 

A `Facility` consists of several `Lanes`. Each `Lane` can be configured to be a different type. The valid lane types are as follows:
- GEN. GENeral purpose lane that accepts cash, credit, and transponders. 
- CC. Credit Card only lane.
- ETC. Electronic Toll Collection Lane for open road tolling. Users are not required to stop in this lane and are billed from their transponders or later by mail
- CASH. Cash-only lanes
- PBM. Pay-by-mail. 
- PMB. Pay-by-mail. Existing vendor uses this convention. 

`Transactions` are distributed to lanes based on rational choice theory, and assume that vehicles will use the shortest lane to which they are qualified. To create a transaction the following information is required:
- Datetime information about when the transaction is loaded into the `Facility`
- pmtType. Payment type, e.g. credit card, pay-by-mail, cash, etc.
- Axel. Axle count for determining the fare and that non-standard axle counts require more work from manual toll collectors. 
- trxID. Transaction ID used to track the transaction through the various queues in this process.


# Output Files
See the sample test simulation in the library for setting up a simulation. Possible outputs include a video file demonstrating the length of queues in various lanes and an `csv` file with the total queues and queues for each lane.

# Tests
This module includes a test suite with a sample `Facility`, `Lanes` and `Transactions`. All transaction processing time calculations use a normal distribution, so the estimated completion times are based on a 99% likelihood of completion. As a result there is a very low probability that tests will fail, so in some rare instances it may require running tests multiple times to pass.

# Utility Class
The utility class provides access to some common methods used by the various other classes
