from ca_counties import california_counties
from datetime import datetime
import dateutil.tz
import json
import requests


PACIFIC_TIME = dateutil.tz.gettz('America/Los_Angeles')


def parse_tableau_json_stream(raw):
    """
    Tableau's data is a series of JSON blobs, each preceded by the number of
    bytes or characters (not sure which) in the JSON blob. The number is
    delimited from the JSON by a semicolon. For example:

        21;{"some": "json data"}16;{"more": "json"}

    This is probably meant to be a streaming format (read up to the semicolon,
    parse the number, read that many more bytes, and emit that data), though we
    are treating it as a complete string here.
    """
    remainder = raw
    chunks = []
    while remainder:
        try:
            size_string, remainder = remainder.split(';', 1)
        except ValueError:
            chunks.append(remainder)
            break
        else:
            size = int(size_string)
            chunk = remainder[:size]
            remainder = remainder[size:]
            data = json.loads(chunk)
            chunks.append(data)
    return chunks


def get_tableau_data(view, subview):
    """
    Load the main data powering a Tableau Dashbaord. Returns a list of
    dictionaries with data (the first is usually overall layout and structure,
    while the second is usually data).

    To find the arguments for this function, find the markup where a Tableau
    dashbaord is embedded on a page. It'll usually be something like:

        <object class="tableauViz" style="display:none;">
            <param name="host_url" value="https://public.tableau.com/">
            <param name="embed_code_version" value="3">
            <param name="site_root" value="">
            <param name="name" value="COVID-19VaccineDashboardPublic/Vaccine">
            <param name="tabs" value="no">
            <param name="toolbar" value="yes">
            <param name="static_image"
                   value="https://public.tableau.com/static/images/CO/COVID-19VaccineDashboardPublic/Vaccine/1.png">
            <param name="animate_transition" value="yes">
            <param name="display_static_image" value="yes">
            <param name="display_spinner" value="yes">
            <param name="display_overlay" value="yes">
            <param name="display_count" value="yes">
            <param name="language" value="en">
            <param name="filter" value="publish=yes">
        </object>

    We care most about the ``<param name="name" `...>`` element. Its ``value``
    attribute contains the view and subview, separated by a forward slash. So
    in the above example, we have:

        <param name="name" value="COVID-19VaccineDashboardPublic/Vaccine">

    And you'd get the corresponding data by calling this function with:

        get_tableau_data('COVID-19VaccineDashboardPublic', 'Vaccine')
    """
    # Use a session because we want to keep cookies around. The first request
    # sets up cookies and generates a session ID, which is needed for the next
    # request, that actually gets the data.
    session = requests.Session()
    dashboard_response = session.get(
        f'https://public.tableau.com/interactive/views/{view}/{subview}',
        params={
            ':embed': 'y',
            ':showVizHome': 'no',
            ':host_url': 'https://public.tableau.com/',
            ':embed_code_version': 3,
            # ':tabs': 'no',
            # ':toolbar': 'yes',
            # ':animate_transition': 'yes',
            # ':display_static_image': 'no',
            # ':display_spinner': 'no',
            # ':display_overlay': 'yes',
            # ':display_count': 'yes',
            # ':language': 'en',
            # 'publish': 'yes',
            # ':loadOrderID': 0,
        },
        # headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0'}
    )
    tableau_session = dashboard_response.headers.get('x-session-id')

    # Load actual data.
    data_url = f'https://public.tableau.com/vizql/w/{view}/v/{subview}/bootstrapSession/sessions/{tableau_session}'
    # TODO: Revisit and trim down the POST data here if possible.
    # There's a lot here, and for the sake of time, I'm just using the data
    # from an actual browser session. There's probably plenty that's not
    # actually required.
    post_data = {
        'worksheetPortSize': '{"w":737,"h":500}',
        'dashboardPortSize': '{"w":737,"h":500}',
        'clientDimension': '{"w":737,"h":550}',
        'renderMapsClientSide': 'true',
        'isBrowserRendering': 'true',
        'browserRenderingThreshold': '100',
        'formatDataValueLocally': 'false',
        'navType': 'Nav',
        'navSrc': 'Boot',
        'devicePixelRatio': '2',
        'clientRenderPixelLimit': '25000000',
        'allowAutogenWorksheetPhoneLayouts': 'false',
        'sheet_id': 'Vaccine',
        'showParams': '{"checkpoint":false,"refresh":false,"refreshUnmodified":false,"unknownParams":":embed_code_version=3&publish=yes"}',
        'stickySessionKey': ('{"dataserverPermissions":"44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",'
                             '"featureFlags":"{\\"MetricsAuthoringBeta\\":false}",'
                             '"isAuthoring":false,'
                             '"isOfflineMode":false,'
                             '"lastUpdatedAt":1613242758888,'
                             '"workbookId":7221037}'),
        'filterTileSize': '200',
        'locale': 'en_US',
        'language': 'en',
        'verboseMode': 'false',
        ':session_feature_flags': '{}',
        'keychain_version': '1',
    }
    data_response = session.post(data_url, data=post_data)

    # NOTE: it *might* be more correct to use data_response.content, but then
    # we need to do some more fancy footwork with character decoding. In the
    # mean time, using the decoded text here actually seems to work fine.
    return parse_tableau_json_stream(data_response.text)


def get_tableau_values(data):
    """
    Tableau's data lists all the values used throughout the view in a single
    place, and the display information about each chart references these values
    by data type (int, cstring, etc.) and index.

    Return a simplified version of this: a dict mapping data types to lists of
    values.
    """
    data_values = (data[1]
                       ['secondaryInfo']
                       ['presModelMap']
                       ['dataDictionary']
                       ['presModelHolder']
                       ['genDataDictionaryPresModel']
                       ['dataSegments']
                       ['0']
                       ['dataColumns'])
    return {valueset['dataType']: valueset['dataValues']
            for valueset in data_values}


def tableau_column_data_value_references(column_data_object):
    return (column_data_object.get('valueIndices') or
            column_data_object.get('aliasIndices') or
            column_data_object['tupleIds'])


def parse_tableau_chart(chart_definition, values_by_type):
    """
    Parse the data underlying a chart in a Tableau dashboard. Returns a list of
    dicts.
    """
    columns = chart_definition['presModelHolder']['genVizDataPresModel']['paneColumnsData']
    definitions = columns['vizDataColumns']
    column_data = columns['paneColumnsList'][0]['vizPaneColumns']

    # Simplify column definitions by calculating the name and joining the
    # references in.
    column_model = [{
        'name': column.get('fieldCaption') or column.get('fn'),
        'dataType': column.get('dataType'),
        'references': tableau_column_data_value_references(column_data[index])
    } for index, column in enumerate(definitions)]

    # Pivot from columns to rows and dereference each value.
    result = []
    for row_index in range(len(column_model[0]['references'])):
        row = {}
        for column in column_model:
            reference = column['references'][row_index]
            if column['dataType']:
                row[column['name']] = values_by_type[column['dataType']][reference]
            else:
                row[column['name']] = reference

        result.append(row)

    return result


def parse_tableau_value_chart(chart_definition, values_by_type, field_name):
    data = parse_tableau_chart(chart_definition,
                               values_by_type)
    return data[0][field_name]


def get_stats_from_tableau():
    """
    Get the top-line stats (administered/shipped/delivered) come from a Tableau
    dashboard.
    """
    data = get_tableau_data('COVID-19VaccineDashboardPublicv2', 'Vaccine')
    values_by_type = get_tableau_values(data)

    charts = (data[1]
                  ['secondaryInfo']
                  ['presModelMap']
                  ['vizData']
                  ['presModelHolder']
                  ['genPresModelMapPresModel']
                  ['presModelMap'])

    county_shots = parse_tableau_chart(charts['County Admin Bar'], values_by_type)
    shots_by_county = {county_key(row['County']): row['SUM(Dose Administered)']
                       for row in county_shots}

    all_tableau_data = {
        'state': {
            'administered': parse_tableau_value_chart(
                charts['Administered'],
                values_by_type,
                'SUM(Dose Administered)'
            ),
            'administered_per_day_avg': parse_tableau_value_chart(
                charts['Administered'],
                values_by_type,
                'SUM(Daily Avg)'
            ),
            'fully_vaccinated': parse_tableau_value_chart(
                charts['Administered'],
                values_by_type,
                'SUM(Fully Vaccinated)'
            ),
            'partially_vaccinated': parse_tableau_value_chart(
                charts['Administered'],
                values_by_type,
                'SUM(Partially Vaccinated)'
            ),
            'delivered': parse_tableau_value_chart(
                charts['Delivered'],
                values_by_type,
                'SUM(Doses Delivered)'
            ),
            'cdc_ltcf_delivered': parse_tableau_value_chart(
                charts['Delivered CDC'],
                values_by_type,
                'SUM(Doses Delivered)'
            ),
        },
        'counties': shots_by_county
    }

    return all_tableau_data


def reformat_grouping(group_data):
    return [{'group': group['CATEGORY'], 'value': group['METRIC_VALUE']}
            for group in group_data]


def get_groupings_for_location(location):
    """
    Stats by category (age, ethnicity, gender) come from separate JSON files
    at well-known URLs for each county.
    """
    race_ethnicity_url = f'https://files.covid19.ca.gov/data/vaccine-equity/race-ethnicity/vaccines_by_race_ethnicity_{location}.json'
    age_url = f'https://files.covid19.ca.gov/data/vaccine-equity/age/vaccines_by_age_{location}.json'
    gender_url = f'https://files.covid19.ca.gov/data/vaccine-equity/gender/vaccines_by_gender_{location}.json'

    race_ethnicity = requests.get(race_ethnicity_url).json()
    age = requests.get(age_url).json()
    gender = requests.get(gender_url).json()

    return {
        'region': location,
        'latest_update': race_ethnicity['meta']['LATEST_ADMIN_DATE'],
        'race_ethnicity': reformat_grouping(race_ethnicity['data']),
        'age': reformat_grouping(age['data']),
        'gender': reformat_grouping(gender['data']),
    }


def get_groupings():
    return {
        'state': get_groupings_for_location('california'),
        'counties': {name: get_groupings_for_location(name)
                     for name in california_counties}
    }


def county_key(name):
    return name.lower().replace(' ', '_')


def cli():
    tableau = get_stats_from_tableau()
    groups = get_groupings()

    state = groups['state'].copy()
    state.update(tableau['state'])

    counties = {}
    for name in california_counties:
        county = groups['counties'][name].copy()
        county['total_administered'] = tableau['counties'][name]
        counties[name] = county

    # TODO: there should probably be some work done to verify that the last
    # updated dates for all the various data sources match and use those dates
    # instead of the current date.
    # One issue here is that it's not clear whether the grouping data files are
    # updated at the same/similar time as the Tableau dashboard. It's also
    # unclear whether the date on the Tableau dashbaord is correct. For
    # example, on 2/14/2021 at 18:53 Pacific, the dashboard reads:
    #
    #     "Data: 2/14/2021 11:59pm | Posted: 2/15/2021"
    #
    # Both these dates are in the future. It could be that this is UTC, or it
    # could just be innacurate. Another questionable point here is that these
    # dates appear in the data, but not the data *time*, which makes it unclear
    # whether "11:59pm" is simply hard-coded.
    result = {
        'date': datetime.now(tz=PACIFIC_TIME).date().isoformat(),
        'state': state,
        'counties': counties
    }

    print(json.dumps(result))


if __name__ == '__main__':
    cli()
