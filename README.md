# fhir-data-synthesis
How to create complete patient health records as FHIR resources with synthea [synthea](https://github.com/synthetichealth/synthea) and how to upload them to a FHIR server 

1. Clone the [synthea repository](https://github.com/synthetichealth/synthea) to any location you choose
2. For FHIR purposes it is necessary to change certain configuration attributes. Follow these instructions on this [website](https://github.com/synthetichealth/synthea/wiki/HL7-FHIR). There are also more information about how FHIR is treated.
3. Create the necessary FHIR resources via the terminal command (you need to be in the cloned repo): `./run_synthea -p 100` (This creates 100 patients with random health records)
4. Add FHIR folder to *fhir_server_interaction*-script 
   1. Copy the absolute path of the *synthea/output/fhir*-folder
   2. Add the path to the *path_to_fhir_resources* 
5. Add the server-credentials (Server_address,username,password)
6. If some error should occur, the count-value is always printed out. With *start_pos* attribute you can define the starting file, so you do not need to upload some resources multiple times  
7. Run the *fhir_server_interaction*-script