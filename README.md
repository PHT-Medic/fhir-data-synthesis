# fhir-data-synthesis
How to create complete patient health records as FHIR resources with synthea [synthea](https://github.com/synthetichealth/synthea) and how to upload them to a FHIR server 

1. Clone the [synthea repository](https://github.com/synthetichealth/synthea) to any location
2. For FHIR purposes it is necessary to change certain configuration attributes. Follow these instructions on this [website](https://github.com/synthetichealth/synthea/wiki/HL7-FHIR). There are also more information about how FHIR needs to be treated.
3. Create the necessary FHIR resources via the terminal command (you need to be in the cloned repo): `./run_synthea -p 100` (This creates 100 patients with random health records)
4. Add FHIR folder to *upload_fhir_resources*-script 
   1. Copy the absolute path of the *synthea/output/fhir*-folder
   2. Add the path to the *path_to_fhir_resources* variable
5. Add the server-credentials (server_address,username,password)
6. If some error occurs, the count/position-value is always printed out of the last uploaded transaction bundle. With the *start_pos* attribute you can define the starting file, so you can skip already uploaded bundles and start over with a different fhir bundle defined with the file position inside the folder.  
7. Run the *upload_fhir_resources*-script
