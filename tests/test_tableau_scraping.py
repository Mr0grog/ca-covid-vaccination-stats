"""
Tests for scraping California's Tableau dashboard.
"""
from ca_covid_vaccination_stats import (get_tableau_data,
                                        get_tableau_values,
                                        parse_tableau_chart)
import json
from pathlib import Path
import pytest


with (Path(__file__).parent / 'sample_tableau_data.json').open() as f:
    SAMPLE_DATA = json.load(f)


@pytest.mark.vcr()
def test_get_tableau_data():
    data = get_tableau_data('COVID-19VaccineDashboardPublic', 'Vaccine')
    # Should return a list of two data objects, the first with basic layout
    # info and the second with detailed data.
    assert len(data) == 2
    assert 'sheetName' in data[0]
    assert data[0]['sheetName'] == 'Vaccine'
    assert 'secondaryInfo' in data[1]


def test_get_tableau_values():
    sample_data = [
        {},
        {
            "secondaryInfo": {
                "presModelMap": {
                    "dataDictionary": {
                        "presModelHolder": {
                            "genDataDictionaryPresModel": {
                                "dataSegments": {
                                    "0": {
                                        "dataColumns": [
                                            {
                                                "dataType": "integer",
                                                "dataValues": [
                                                    123,
                                                    456,
                                                    789
                                                ]
                                            },
                                            {
                                                "dataType": "real",
                                                "dataValues": [
                                                    1.234,
                                                    2.878
                                                ]
                                            },
                                            {
                                                "dataType": "cstring",
                                                "dataValues": [
                                                    "hello"
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ]
    values_by_type = get_tableau_values(sample_data)
    assert values_by_type == {
        'integer': [123, 456, 789],
        'real': [1.234, 2.878],
        'cstring': ['hello']
    }


def test_parse_tableau_chart():
    values_by_type = get_tableau_values(SAMPLE_DATA)
    chart = (SAMPLE_DATA[1]
                        ['secondaryInfo']
                        ['presModelMap']
                        ['vizData']
                        ['presModelHolder']
                        ['genPresModelMapPresModel']
                        ['presModelMap']
                        ['County Admin Bar'])
    data = parse_tableau_chart(chart, values_by_type)
    assert data == [
        {'AGG(Total Doses Administered)': 365,
         'County': 'Alpine',
         '[system:visual].[tuple_id]': 1},
        {'AGG(Total Doses Administered)': 756,
         'County': 'Sierra',
         '[system:visual].[tuple_id]': 2},
        {'AGG(Total Doses Administered)': 1174,
         'County': 'Mariposa',
         '[system:visual].[tuple_id]': 3},
        {'AGG(Total Doses Administered)': 1179,
         'County': 'Trinity',
         '[system:visual].[tuple_id]': 4},
        {'AGG(Total Doses Administered)': 1513,
         'County': 'Modoc',
         '[system:visual].[tuple_id]': 5},
        {'AGG(Total Doses Administered)': 1912,
         'County': 'Colusa',
         '[system:visual].[tuple_id]': 6},
        {'AGG(Total Doses Administered)': 2066,
         'County': 'Plumas',
         '[system:visual].[tuple_id]': 7},
        {'AGG(Total Doses Administered)': 2528,
         'County': 'Inyo',
         '[system:visual].[tuple_id]': 8},
        {'AGG(Total Doses Administered)': 2657,
         'County': 'Del Norte',
         '[system:visual].[tuple_id]': 9},
        {'AGG(Total Doses Administered)': 2883,
         'County': 'Lassen',
         '[system:visual].[tuple_id]': 10},
        {'AGG(Total Doses Administered)': 3733,
         'County': 'Glenn',
         '[system:visual].[tuple_id]': 11},
        {'AGG(Total Doses Administered)': 5898,
         'County': 'Mono',
         '[system:visual].[tuple_id]': 12},
        {'AGG(Total Doses Administered)': 5938,
         'County': 'Amador',
         '[system:visual].[tuple_id]': 13},
        {'AGG(Total Doses Administered)': 5984,
         'County': 'San Benito',
         '[system:visual].[tuple_id]': 14},
        {'AGG(Total Doses Administered)': 6143,
         'County': 'Tehama',
         '[system:visual].[tuple_id]': 15},
        {'AGG(Total Doses Administered)': 6652,
         'County': 'Calaveras',
         '[system:visual].[tuple_id]': 16},
        {'AGG(Total Doses Administered)': 6694,
         'County': 'Yuba',
         '[system:visual].[tuple_id]': 17},
        {'AGG(Total Doses Administered)': 7417,
         'County': 'Siskiyou',
         '[system:visual].[tuple_id]': 18},
        {'AGG(Total Doses Administered)': 9017,
         'County': 'Lake',
         '[system:visual].[tuple_id]': 19},
        {'AGG(Total Doses Administered)': 9217,
         'County': 'Tuolumne',
         '[system:visual].[tuple_id]': 20},
        {'AGG(Total Doses Administered)': 9443,
         'County': 'Kings',
         '[system:visual].[tuple_id]': 21},
        {'AGG(Total Doses Administered)': 13471,
         'County': 'Sutter',
         '[system:visual].[tuple_id]': 22},
        {'AGG(Total Doses Administered)': 15065,
         'County': 'Nevada',
         '[system:visual].[tuple_id]': 23},
        {'AGG(Total Doses Administered)': 16275,
         'County': 'Madera',
         '[system:visual].[tuple_id]': 24},
        {'AGG(Total Doses Administered)': 16721,
         'County': 'Imperial',
         '[system:visual].[tuple_id]': 25},
        {'AGG(Total Doses Administered)': 18543,
         'County': 'Mendocino',
         '[system:visual].[tuple_id]': 26},
        {'AGG(Total Doses Administered)': 20704,
         'County': 'Shasta',
         '[system:visual].[tuple_id]': 27},
        {'AGG(Total Doses Administered)': 22010,
         'County': 'Humboldt',
         '[system:visual].[tuple_id]': 28},
        {'AGG(Total Doses Administered)': 22517,
         'County': 'Merced',
         '[system:visual].[tuple_id]': 29},
        {'AGG(Total Doses Administered)': 29341,
         'County': 'El Dorado',
         '[system:visual].[tuple_id]': 30},
        {'AGG(Total Doses Administered)': 32222,
         'County': 'Napa',
         '[system:visual].[tuple_id]': 31},
        {'AGG(Total Doses Administered)': 35498,
         'County': 'Yolo',
         '[system:visual].[tuple_id]': 32},
        {'AGG(Total Doses Administered)': 40862,
         'County': 'Tulare',
         '[system:visual].[tuple_id]': 33},
        {'AGG(Total Doses Administered)': 41438,
         'County': 'San Luis Obispo',
         '[system:visual].[tuple_id]': 34},
        {'AGG(Total Doses Administered)': 42312,
         'County': 'Butte',
         '[system:visual].[tuple_id]': 35},
        {'AGG(Total Doses Administered)': 47595,
         'County': 'Monterey',
         '[system:visual].[tuple_id]': 36},
        {'AGG(Total Doses Administered)': 53044,
         'County': 'Santa Cruz',
         '[system:visual].[tuple_id]': 37},
        {'AGG(Total Doses Administered)': 57758,
         'County': 'Marin',
         '[system:visual].[tuple_id]': 38},
        {'AGG(Total Doses Administered)': 64625,
         'County': 'Santa Barbara',
         '[system:visual].[tuple_id]': 39},
        {'AGG(Total Doses Administered)': 65368,
         'County': 'Stanislaus',
         '[system:visual].[tuple_id]': 40},
        {'AGG(Total Doses Administered)': 66580,
         'County': 'Solano',
         '[system:visual].[tuple_id]': 41},
        {'AGG(Total Doses Administered)': 77793,
         'County': 'Placer',
         '[system:visual].[tuple_id]': 42},
        {'AGG(Total Doses Administered)': 78556,
         'County': 'San Joaquin',
         '[system:visual].[tuple_id]': 43},
        {'AGG(Total Doses Administered)': 83637,
         'County': 'Kern',
         '[system:visual].[tuple_id]': 44},
        {'AGG(Total Doses Administered)': 93026,
         'County': 'Sonoma',
         '[system:visual].[tuple_id]': 45},
        {'AGG(Total Doses Administered)': 122913,
         'County': 'Fresno',
         '[system:visual].[tuple_id]': 46},
        {'AGG(Total Doses Administered)': 123036,
         'County': 'Ventura',
         '[system:visual].[tuple_id]': 47},
        {'AGG(Total Doses Administered)': 139963,
         'County': 'San Mateo',
         '[system:visual].[tuple_id]': 48},
        {'AGG(Total Doses Administered)': 152599,
         'County': 'San Francisco',
         '[system:visual].[tuple_id]': 49},
        {'AGG(Total Doses Administered)': 202648,
         'County': 'Sacramento',
         '[system:visual].[tuple_id]': 50},
        {'AGG(Total Doses Administered)': 214056,
         'County': 'Contra Costa',
         '[system:visual].[tuple_id]': 51},
        {'AGG(Total Doses Administered)': 248849,
         'County': 'San Bernardino',
         '[system:visual].[tuple_id]': 52},
        {'AGG(Total Doses Administered)': 249086,
         'County': 'Alameda',
         '[system:visual].[tuple_id]': 53},
        {'AGG(Total Doses Administered)': 294174,
         'County': 'Riverside',
         '[system:visual].[tuple_id]': 54},
        {'AGG(Total Doses Administered)': 306150,
         'County': 'Santa Clara',
         '[system:visual].[tuple_id]': 55},
        {'AGG(Total Doses Administered)': 499904,
         'County': 'Orange',
         '[system:visual].[tuple_id]': 56},
        {'AGG(Total Doses Administered)': 594674,
         'County': 'San Diego',
         '[system:visual].[tuple_id]': 57},
        {'AGG(Total Doses Administered)': 1471587,
         'County': 'Los Angeles',
         '[system:visual].[tuple_id]': 58},
    ]
