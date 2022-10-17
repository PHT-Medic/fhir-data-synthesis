from fhir_kindling import FhirServer
from fhir_kindling.serde.flatten import flatten_resources
from requests.auth import HTTPBasicAuth
import time
from datetime import timedelta
from os import listdir
from os.path import isfile, join
import requests
import re

server_address = "https://dev-fhir.grafm.de/blaze-1"
username = "pht-dev"
password = "start123"

path_to_fhir_resources = "C:\\Users\\FStrothmann\\Downloads\\synthea\\output\\fhir"
start_pos = 0
headers = {"Content-Type": "application/fhir+json;charset=utf-8"}

def load_files(path):
    '''
    collects all file names of a certain folder

    :param path: absolute path of the folder with the transaction_bundels of synthesised patient health records
    :return:
        hospital_file: Single file path for all the hospital information
        paractitioner_file_ single file path for all the practitioner informations
        files: all other patient health record files
    '''
    files = [f for f in listdir(path) if isfile(join(path, f))]
    regex_hospital = re.compile(r'hospitalInformation')
    regex_practitioner = re.compile(r'practitionerInformation')
    hospital_file = [ele for ele in files if regex_hospital.match(ele)][0]
    practitioner_file = [ele for ele in files if regex_practitioner.match(ele)][0]
    files.remove(hospital_file)
    files.remove(practitioner_file)
    return hospital_file,practitioner_file,files

def upload_bundle(bundle_path, server_address, basic, headers):
    '''
    Uploads a single transaction bundle to the fhir server
    Throws IOError for general mistakes
    Throws UnicodeEncodeError for incorrect files
    :param bundle_path: absolute path to a single file of a patient health record
    :param server_address: server_address where all the fhir resources should be uploaded to
    :param basic: authencification credentials
    :param headers: defines how the header is structured
    :return: ---
    '''
    try:
        with open(bundle_path, encoding="utf8") as f:
            bundle_file_content = f.read()
            r = requests.post(url=server_address, data=bundle_file_content, headers=headers, auth=basic)
    except IOError:
        print("IOError with: " + bundle_path)
    except UnicodeEncodeError:
        print("UnicodeEncodeError with: " + bundle_path)

def complete_upload_stream(server_address, username, password, headers,path,count_value=0):
    '''
    upload of a whole folder with patient health records in FHIR format

    :param server_address: server address where the fhir resources should be uploaded to
    :param username: username for addressing the server
    :param password: password for addressing the server
    :param headers: defines how the header is structured
    :param path: absolute path to the folder
    :param count_value: starting value of which file the upload should begin with
    :return: ---
    '''
    hospital_file,practitioner_file,files = load_files(path)
    counter = count_value
    basic = HTTPBasicAuth(username, password)
    # First upload the basic resources. The references to practitioner and hospital are necessary
    # But if there was an issue and you want to restart at certain file-count, then those information are already uploaded
    if(count_value == 0):
        upload_bundle(path + "\\" + hospital_file, server_address, basic, headers)
        upload_bundle(path + "\\" + practitioner_file, server_address, basic, headers)
    del files[:counter]
    for file in files:
        upload_bundle(path + "\\" + file, server_address, basic, headers)
        print(counter,". File: ",file)
        counter += 1

if __name__ == '__main__':
    time_start = time.time()

    basic_auth_server = FhirServer(server_address,username,password,timeout=36000)
    complete_upload_stream(server_address=server_address,username=username,password=password,headers=headers,path=path_to_fhir_resources,count_value=start_pos)

    time_end = time.time()
    print(f'Time start: {time.asctime(time.localtime(time_start))}')
    print(f'Time end: {time.asctime(time.localtime(time_end))}')
    print(f'Time diff: {str(timedelta(seconds=(time_end - time_start)))}')