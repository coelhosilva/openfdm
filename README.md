# openFOQA


`openfoqa` is a production-ready Python package for Flight Operations Quality Assurance (FOQA) event identification.

It provides:
-   An implementation of a FOQA pipeline for batch processing of FOQA events across multiple flights;
-   A rule engine with base events and an extensible software architecture;
-   A standardized flight dataframe and parameters model;
-   Extensible connectors for loading flights and saving outputs of FOQA events.

## Installation

The easiest way to install `openfoqa` is using pip from your virtual environment.

Directly from GitHub:

`pip install git+https://github.com/coelhosilva/openfoqa.git`

## Examples

This is a sample usage of the package for constructing a FOQA pipeline. It loads two sample flights 
from disk and calculate the outputs of the following FOQA events: hard landing, bounced landing, and 
landing in a crab.

```python
from openfoqa.rule_engine import (
    HardLandingEvent,
    BouncedLandingEvent,
    LandingInACrabEvent,
)
from openfoqa.processor.pipeline import FOQAPipeline
from openfoqa.processor.connectors.flight_loader import SampleFlightLoader
from openfoqa.processor.connectors.output_connector import ConsoleOutputConnector


foqa_pipeline = FOQAPipeline(
    flight_loader=SampleFlightLoader(),
    foqa_events=[
        HardLandingEvent(),
        BouncedLandingEvent(),
        LandingInACrabEvent(),
    ],
    output_connector=ConsoleOutputConnector(),
)

foqa_pipeline.run()
```


## Contributions

We welcome and encourage new contributors to help test `openfoqa` and add new functionality. Any input, feedback, 
bug report or contribution is welcome.

If one wishes to contact the author, they may do so by emailing coelho@ita.br.