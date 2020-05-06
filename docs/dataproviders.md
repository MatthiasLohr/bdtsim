# Data Providers

Data Providers allow the simulation of protocols regarding trading with different kind of data
(e.g. binary data vs. XML documents).

## RandomDataProvider

This data provider generates pseudo-random binary data.
Data generation is controlled by a (constant) seed.
To modify the data, provide another seed value.


### Parameters

  * `size`: File size, provided as number of bytes or in the form like `1k`, `1M`, ...
  * `seed`: Initialization value for random generator


## FileDataProvider

File data provider provides the contents of an actual file to the simulation.

### Parameters

  * `filename`: Name of the file to be used in simulation.
