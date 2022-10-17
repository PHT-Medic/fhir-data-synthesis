import time
from datetime import timedelta
from typing import Tuple
import csv
from fhir_kindling.serde.flatten import flatten_resources
import pandas as pd
from fhir_kindling import FhirServer

server_address = "https://dev-fhir.grafm.de/blaze-1"
username = "pht-dev"
password = "start123"
csv_file_name = "blaze-1_results"


def get_available_resources(address, user, pw, order_asc=True) -> pd.DataFrame:
    """
    returns all available resources
    :param address: address of the fhir server
    :param user: username credential for the server
    :param pw: password credentials for the server
    :param order_asc: bool-value to define how to sort the resources
    :return: a list of all available resources as list
    """
    basic_auth_server = FhirServer(address, user, pw, timeout=36000)
    if order_asc:
        resourceList = sorted(basic_auth_server.summary().available_resources, key=lambda x: x.count)
    else:
        resourceList = sorted(basic_auth_server.summary().available_resources, key=lambda x: x.count, reverse=True)
    all_resources = []
    for val in resourceList:
        all_resources.append({'resource': val.resource, 'count': val.count})
    df = pd.DataFrame(all_resources, columns=["resource", "count"])
    df['count'] = df.apply(lambda x: "{:,}".format(x['count']), axis=1)

    return df


def get_resource(address, user, pw, resourceType) -> Tuple[pd.DataFrame, dict]:
    """
    Downloading all available instances of a resource type, flatten it and retrieve the time how long it processed it
    :param address: server address
    :param user: username credential for the fhir server
    :param pw: pw credential for the fhir server
    :param resourceType: specified the resource type you looking for
    :return: tuple of 1. pd.Dataframe with all flattened resources and 2. a dictionary of the gathered types
    """
    # Connect with basic auth
    start = time.time()
    basic_auth_server = FhirServer(address, user, pw, timeout=36000)
    print(f"Run query for {resourceType}")
    query_results = basic_auth_server.query(resourceType, output_format="json").all()
    query_time = time.time()
    print(f"Start Flattening for {resourceType}\n")
    flatted_resources = flatten_resources(query_results.resources)
    end = time.time()
    query_diff_time = timedelta(seconds=(query_time - start))
    flatten_diff_time = timedelta(seconds=(end - query_time))
    diff_time = timedelta(seconds=(end - start))
    times = {"start_time": time.asctime(time.localtime(start)), "end_time": time.asctime(time.localtime(end)),
             "total_diff": diff_time, "query_time": query_diff_time,
             'flatten_time': flatten_diff_time}
    return flatted_resources, times


def create_csv_of_downloading_and_flattening_resources(address, user, pw, saveFile_name, order_asc):
    """
    creates a csv-file with collected time data for each available resource of the given fhir server
    :param address: server address
    :param user: username credential for the fhir server
    :param pw: password credential for the fhir server
    :param saveFile_name: name of the resulting csv-file
    :param order_asc: order of the count value in which the available resource will be processed
    :return: ---
    """
    resource_types = get_available_resources(address, user, pw, order_asc=order_asc)
    except_list = []
    result_list = []

    for index, row in resource_types.iterrows():
        resource = row['resource']
        count = row['count']
        dict_val = {"resource": resource, "count": count}
        try:
            _, times = get_resource(address, user, pw, resource)
            dic = dict_val | times
            result_list.append(dic)
        except Exception as e:
            except_list.append({"resource": resource, "exception": str(e)})

    df = pd.DataFrame(result_list)
    df.to_csv(f'./{saveFile_name}.csv', index=False)
    if len(except_list) != 0:
        keys = except_list[0].keys()
        with open(f'./{saveFile_name}_exceptions.csv', 'w', newline='') as error_file:
            dict_writer = csv.DictWriter(error_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(except_list)


if __name__ == '__main__':
    time_start = time.time()
    resources = get_available_resources(server_address, username, password, False)
    print("All available resources with the total number each")
    print(resources)

    create_csv_of_downloading_and_flattening_resources(server_address, username, password, csv_file_name, True)

    time_end = time.time()
    print(f'Time start: {time.asctime(time.localtime(time_start))}')
    print(f'Time end: {time.asctime(time.localtime(time_end))}')
    print(f'Time diff: {str(timedelta(seconds=(time_end - time_start)))}')
