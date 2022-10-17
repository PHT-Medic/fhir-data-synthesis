import re
import time
from datetime import timedelta
from os import listdir
from os.path import isfile, join
import requests
from fhir_kindling import FhirServer
from requests.auth import HTTPBasicAuth

server_address = "https://dev-fhir.grafm.de/blaze-1"
username = "pht-dev"
password = "start123"

path_to_fhir_resources = "C:\\Users\\FStrothmann\\Downloads\\synthea\\output\\fhir"
start_pos = 0
headers = {"Content-Type": "application/fhir+json;charset=utf-8"}


def load_files(path):
    """
    collects all file names of a certain folder
    :param path: absolute path of the folder with the transaction_bundles of synthesised patient health records
    :return:
        hospital_file: Single file path for all the hospital information
        practitioner_file_ single file path for all the practitioner information
        files: all other patient health record files
    """

    files = [f for f in listdir(path) if isfile(join(path, f))]
    regex_hospital = re.compile(r'hospitalInformation')
    regex_practitioner = re.compile(r'practitionerInformation')
    hospital_file = [ele for ele in files if regex_hospital.match(ele)][0]
    practitioner_file = [ele for ele in files if regex_practitioner.match(ele)][0]
    files.remove(hospital_file)
    files.remove(practitioner_file)
    return hospital_file, practitioner_file, files


def upload_bundle(bundle_path, address, basic, header):
    """
    Uploads a single transaction bundle to the fhir server
    Throws IOError for general mistakes
    Throws UnicodeEncodeError for incorrect files
    :param bundle_path: absolute path to a single file of a patient health record
    :param address: server_address where all the fhir resources should be uploaded to
    :param basic: authentication credentials
    :param header: defines how the header is structured
    :return: ---
    """
    try:
        with open(bundle_path, encoding="utf8") as f:
            bundle_file_content = f.read()
            _ = requests.post(url=address, data=bundle_file_content, headers=header, auth=basic)
    except IOError:
        print("IOError with: " + bundle_path)
    except UnicodeEncodeError:
        print("UnicodeEncodeError with: " + bundle_path)


def complete_upload_stream(address, user, pw, header, path, count_value=0):
    """
    upload of a whole folder with patient health records in FHIR format
    :param address: server address where the fhir resources should be uploaded to
    :param user: username for addressing the server
    :param pw: password for addressing the server
    :param header: defines how the header is structured
    :param path: absolute path to the folder
    :param count_value: starting value of which file the upload should begin with
    :return:
    """

    hospital_file, practitioner_file, files = load_files(path)
    counter = count_value
    basic = HTTPBasicAuth(user, pw)
    # First upload the basic resources. The references to practitioner and hospital are necessary but if there was an
    # issue, and you want to restart at certain file-count, then this information is already uploaded
    if count_value == 0:
        upload_bundle(path + "\\" + hospital_file, address, basic, header)
        upload_bundle(path + "\\" + practitioner_file, address, basic, header)
    del files[:counter]
    for file in files:
        upload_bundle(path + "\\" + file, address, basic, header)
        print(counter, ". File: ", file)
        counter += 1


if __name__ == '__main__':
    time_start = time.time()
    basic_auth_server = FhirServer(server_address, username, password, timeout=36000)
    complete_upload_stream(address=server_address, user=username, pw=password, header=headers,
                           path=path_to_fhir_resources, count_value=start_pos)

    time_end = time.time()
    print(f'Time start: {time.asctime(time.localtime(time_start))}')
    print(f'Time end: {time.asctime(time.localtime(time_end))}')
    print(f'Time diff: {str(timedelta(seconds=(time_end - time_start)))}')
