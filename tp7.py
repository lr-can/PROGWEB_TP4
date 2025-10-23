"""
This script is an extension of TP4, as it will provide additional functionalities i.e. a Web API.
"""
import sql_requests
import sqlite3

def gene_by_id(id):
    """
    Fetches gene information, its transcripts, and associated expression data for a given gene ID.
    This function is intended to be used as part of a Web API to provide gene data in
    a structured format (e.g., JSON).
    Args:
        id (str): The Ensembl gene ID to fetch information for.
    Returns:
        dict: A dictionary containing:
            - "gene_info": A dictionary with gene information.  
            - "transcript_info": A list of dictionaries, each containing transcript information.
            - "parts_info": A list of dictionaries, each containing distinct atlas organism parts
                where the gene is expressed.
    If the gene ID does not exist, returns (None, None, None).

    """
    gene_info, transcript_info, parts_info = sql_requests.fetch_gene_by_id(id)

    # Note : info will be None if gene_id does not exist
    if gene_info is None:
        return None # then tp4's route will handle the 404 error
    
    buffer = {}
    for info in gene_info.keys():
        buffer[info] = gene_info[info]
    
    buffer["transcript"] = []
    for transcript in transcript_info:
        transcript_dict = {}
        for info in transcript.keys():
            transcript_dict[info] = transcript[info]
        buffer["transcript"].append(transcript_dict)
    
    buffer["parts"] = []
    for part in parts_info:
        buffer["parts"].append(part["atlas_organism_part"])

    # Return data as dictionaries for easier JSON serialization
    return buffer

def collection_of_genes(offset=0):
    """
    Fetches a collection of distinct genes and their associated names with pagination.
    This function is intended to be used as part of a Web API to provide gene data in
    a structured format (e.g., JSON).
    Args:
        offset (int): The offset for pagination.
    Returns:
        list of dict: A list of dictionaries, each containing distinct gene information
            and their associated names.
    """
    rows = sql_requests.fetch_collection_of_genes(offset)
    return [dict(row) for row in rows]

def verification_data_gene(data):
    """
    Verifies if the provided gene data contains all required fields.
    Args:
        data (dict): The gene data to be verified.
    Returns:
        int: The HTTP response code indicating the result of the verification.
    """
    resp_code = 201  # Created
        # Data validation
    required_fields = ["Ensemble_Gene_ID", "Chromosome_Name", "Band", "Gene_Start",  "Gene_End"]

    if len([field for field in required_fields if field not in data]) > 0:
        resp_code = 400  # Bad Request
    
    if type(data["Gene_Start"]) is not int or type(data["Gene_End"]) is not int:
        resp_code = 400  # Bad Request
    
    if data["Gene_Start"] < 0 or data["Gene_End"] < 0 or data["Gene_Start"] > data["Gene_End"]:
        resp_code = 400  # Bad Request
    
    if "Strand" in data and type(data["Strand"]) is not int:
        resp_code = 400  # Bad Request
    
    if "Associated_Gene_Name" in data and type(data["Associated_Gene_Name"]) is not str:
        resp_code = 400  # Bad Request

    if len(data.keys()) > len(required_fields) + 2:  # +2 for optional fields
        resp_code = 400  # Bad Request

    resp_code = 409 if sql_requests.check_gene_exists(data["Ensemble_Gene_ID"]) else resp_code

    return resp_code


def edition_gene(mode, data, gene_id=None):
    """
    Edits gene data in the database based on the specified mode.
    Args:
        mode (str): The mode of operation. Can be "new" for inserting new genes
            or "delete" for deleting existing genes.
        data (dict or list): The gene data to be processed. For "new" mode, it can be
            a dictionary representing a single gene or a list of such dictionaries. For "delete" mode,
            it should be a dictionary containing the "Ensemble_Gene_ID" of the gene to be deleted.
        gene_id (str, optional): The gene ID for update operations. Defaults to None.
    Returns:
        int: The HTTP response code indicating the result of the operation.
    """
    # Note : could use match case in Python 3.10+ but keeping it simple for compatibility
    if mode == "new" and type(data) is dict:
        resp_code = verification_data_gene(data)
        if resp_code == 201:
            try:
                sql_requests.insert_new_gene(
                    data["Ensemble_Gene_ID"],
                    data["Chromosome_Name"],
                    data["Band"],
                    data["Gene_Start"],
                    data["Gene_End"],
                    data.get("Strand"),
                    data.get("Associated_Gene_Name")
                )
            except:
                resp_code = 500  # Internal Server Error (e.g., DB constraint violation)
    elif mode == "new" and type(data) is list:
        """
        NOT OPTIMIZED FOR BULK INSERTION, just a simple implementation to
        handle multiple gene insertions via a list of dicts.

        for item in data:
            resp_code = edition_gene("new", item) # Recursive call for each item
            if resp_code != 201:
                break # Stop at first error
        """
        """
        Creating bulk insertion with transaction management
        """
        resp_code = 201  # Created
        bulk = []
        for item in data:
            code = verification_data_gene(item)
            if code != 201:
                resp_code = code
                break
            bulk.append(item)
        bulks_size = 100
        for i in range(0, len(bulk), bulks_size):
            chunk = bulk[i:i+bulks_size]
            try:
                sql_requests.insert_bulk_new_genes(chunk)
            except:
                resp_code = 500  # Internal Server Error (e.g., DB constraint violation)
                break

    elif mode == "delete":
        resp_code = 200  # OK
        if not sql_requests.check_gene_exists(data["Ensemble_Gene_ID"]):
            resp_code = 404 # Not Found
            resp_code = 200 # According to the instruction, always return 200
        else:
            try:
                sql_requests.delete_gene(data["Ensemble_Gene_ID"])
            except:
                resp_code = 500  # Internal Server Error (e.g., DB constraint violation)
            finally:
                resp_code = 200 # According to the instruction

    # Pour aller plus loin : implement "update" mode here
    elif mode == "update":
        resp_code = verification_data_gene(data)
        if gene_id != data["Ensemble_Gene_ID"]:
            resp_code = 400  # Bad Request

        # Check if gene exists for update
        if resp_code in [201, 409]:
            resp_code = 200 if resp_code == 409 else 201 # OK (updated or Created)
        
        # If gene does not exist, create it
        if resp_code == 201:
            try:
                sql_requests.insert_new_gene(
                    data["Ensemble_Gene_ID"],
                    data["Chromosome_Name"],
                    data["Band"],
                    data["Gene_Start"],
                    data["Gene_End"],
                    data.get("Strand"),
                    data.get("Associated_Gene_Name")
                )
            except:
                resp_code = 500  # Internal Server Error (e.g., DB constraint violation)
        # If gene exists, update it
        elif resp_code == 200:
            try:
                sql_requests.update_gene(
                    data["Ensemble_Gene_ID"],
                    data["Chromosome_Name"],
                    data["Band"],
                    data["Gene_Start"],
                    data["Gene_End"],
                    data.get("Strand"),
                    data.get("Associated_Gene_Name")
                )
            except:
                resp_code = 500  # Internal Server Error (e.g., DB constraint violation)
    else:
        resp_code = 400  # Bad Request (invalid mode)




    return resp_code
        
