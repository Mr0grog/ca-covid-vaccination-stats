⚠️ **This project is deprecated!** ⚠️ Since I wrote this scraper, the State of California has started publishing actual machine-readable data at: https://data.ca.gov/dataset/covid-19-vaccine-progress-dashboard-data. There’s no reason for anyone to continue to use the data this scraper produces.


# CA COVID Vaccination Stats

This project scrapes and stores a running timeseries of state & county level COVID-19 vaccination statistics in California from https://covid19.ca.gov/vaccines/.

The State of California currently publishes more detailed statistics on a county level than most county health agencies are publishing, but there are two big caveats:

1. ~This data is not [yet?] in the state’s data portal or Snowflake, so it has to be scraped.~ *(Update: this is now available in state data portal at https://data.ca.gov/dataset/covid-19-vaccine-progress-dashboard-data)*
2. ~The data is only provided as a point-in-time snapshot of the numbers, so you can’t evaluate historical trends.~ *(Update: the new state data portal resource includes historical data.)*

This project aims to overcome both those barriers by turning the CA state website’s content into machine readable data and updating it on a daily basis to build a timeseries for the state and each county.


## Usage

You probably shouldn’t run the scraper unless you are helping to develop it! Instead, you should use the data it outputs.


## Installation

1. First, install Python 3.8 or later.

2. Clone this repo and switched to the cloned directory.

    ```sh
    $ git clone <url_for_this_repo>
    $ cd ca_covid_vaccination_stats
    ```

3. (Optional) set up a virtual environment. There are a lot of tools for this, but I recommend [`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv). (You might also use venv or Conda/Anaconda.)

4. Install requirements with `pip`.

    ```sh
    $ pip install -r requirements.txt
    ```

5. Run the scraper!

    ```sh
    $ python ca_covid_vaccination_stats.py
    ```


## License

ca_covid_vaccination_stats is open source software. It is (c) 2021 Rob Brackett and licensed under the BSD license. The full license text is in the LICENSE file.
