# openFDM


`openfdm` is a production-ready Python package for running a Flight Data Monitoring (FDM)/Flight Operations Quality Assurance (FOQA) program, including the identification of safety events.

It provides:
-   An implementation of a FDM pipeline for batch processing of safety events across multiple flights;
-   A rule engine with base events and an extensible software architecture;
-   A standardized flight dataframe and parameters model;
-   Extensible connectors for loading flights and saving outputs of business rules.

## Installation

The easiest way to install `openfdm` is using pip from your virtual environment.

Directly from GitHub:

`pip install git+https://github.com/coelhosilva/openfdm.git`

## Examples

This is a sample usage of the package for constructing a FDM pipeline. It loads two sample flights 
from disk and calculate the outputs of the following safety events: hard landing, bounced landing, and 
landing in a crab.

```python
from openfdm.rule_engine.safety import (
    HardLandingEvent,
    BouncedLandingEvent,
    LandingInACrabEvent,
)
from openfdm.processor.pipeline import FlightDataMonitoringPipeline
from openfdm.processor.connectors.flight_loader import SampleFlightLoader
from openfdm.processor.connectors.output_connector import ConsoleOutputConnector


fdm_pipeline = FlightDataMonitoringPipeline(
    flight_loader=SampleFlightLoader(),
    fdm_events=[
        HardLandingEvent(),
        BouncedLandingEvent(),
        LandingInACrabEvent(),
    ],
    output_connector=ConsoleOutputConnector(),
)

fdm_pipeline.run()
```


## Contributions

We welcome and encourage new contributors to help test `openfdm` and add new functionality. Any input, feedback, 
bug report or contribution is welcome.

If one wishes to contact the author, they may do so by emailing coelho@ita.br.