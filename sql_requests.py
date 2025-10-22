import sqlite3
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend

def get_db_connection():
    """
    Establishes a connection to the SQLite database and sets the row factory
    to sqlite3.Row for dictionary-like access to rows.
    Returns:
        sqlite3.Connection: The database connection object. 
    """
    conn = sqlite3.connect("ensembl_hs63_simple.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


def fetch_for_index():
    """
    Fetches distinct atlas organism parts from the Expression table.
    Returns:
        list of sqlite3.Row: A list of rows containing distinct atlas organism parts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT DISTINCT atlas_organism_part FROM Expression WHERE atlas_organism_part IS NOT NULL ORDER BY "atlas_organism_part" ASC
                   """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_genes_by_part(part):
    """
    Fetches distinct genes and their associated names for a given atlas organism part.
    Args:
        part (str): The atlas organism part to filter genes by.
    Returns:
        list of sqlite3.Row: A list of rows containing distinct genes and their associated names.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT g.ensembl_gene_id, associated_gene_name
    FROM Genes as g
    NATURAL JOIN Transcripts as t
    NATURAL JOIN Expression as e
    WHERE atlas_organism_part = ?
    ORDER BY g.ensembl_gene_id
                   """, (part,))
    rows = cursor.fetchall()
    print(rows[1].keys())
    conn.close()
    return rows

def fetch_gene_by_id(gene_id):
    """
    Fetches gene information, its transcripts, and associated expression data for a given gene ID.
    Args:
        gene_id (str): The Ensembl gene ID to fetch information for.
    Returns:
        tuple: A tuple containing:
            - sqlite3.Row: The gene information.
            - list of sqlite3.Row: A list of transcripts associated with the gene.
            - list of sqlite3.Row: A list of distinct atlas organism parts where the gene is
                expressed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
    FROM Genes as g
    WHERE g.ensembl_gene_id = ?
                   """, (gene_id,))
    row = cursor.fetchone()
    cursor.execute("""
        SELECT *
    FROM Transcripts as t
    WHERE t.ensembl_gene_id = ?
                     """, (gene_id,))
    transcripts = cursor.fetchall()
    list_of_transcript_ids = [
        transcript['ensembl_transcript_id'] for transcript in transcripts
    ]
    row2 = transcripts
    cursor.execute("""
        SELECT DISTINCT e.atlas_organism_part
        FROM Expression as e
        INNER JOIN Transcripts t
        ON e.ensembl_transcript_id = t.ensembl_transcript_id
        WHERE t.ensembl_transcript_id IN ({}) AND e.atlas_organism_part IS NOT NULL
    """.format(",".join("?" for _ in list_of_transcript_ids)), tuple(list_of_transcript_ids))
    rows3 = cursor.fetchall()
    conn.close()
    return row, row2, rows3 # would need to name them otherwise

def update_gene(gene_id, form_data):
    """
    Updates gene information in the database for a given gene ID using provided form data.
    Args:
        gene_id (str): The Ensembl gene ID to update.
        form_data (dict): A dictionary containing the updated gene information.
    Returns:
        None    
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Genes
        SET Chromosome_Name = ?,
            Band = ?,
            Strand = ?,
            Gene_Start = ?,
            Gene_End = ?
        WHERE ensembl_gene_id = ?
    """, (
        form_data['chromosome_name'],
        form_data['band'],
        form_data['strand'],
        form_data['gene-start'],
        form_data['gene-end'],
        gene_id))
    conn.commit()
    conn.close()
    return

def from_list_to_dict(keys, values):
    """
    Helper function that:
    Converts two lists into a dictionary by zipping them together.
    Args:
        keys (list): A list of keys.
        values (list): A list of values.
    Returns:
        dict: A dictionary mapping keys to values.
    """
    return {key: value for key, value in zip(keys, values)}

def fetch_transcript_by_id(transcript_id):
    """
    Fetches transcript information and associated expression data for a given transcript ID.
    Args:
        transcript_id (str): The Ensembl transcript ID to fetch information for.
    Returns:
        tuple: A tuple containing:
            - sqlite3.Row: The transcript information.
            - list of sqlite3.Row: A list of expression data associated with the transcript.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
    FROM Transcripts as t
    WHERE t.ensembl_transcript_id = ?
                   """, (transcript_id,))
    row1 = cursor.fetchone() # only one transcript per id
    cursor.execute("""
        SELECT *
    FROM Expression as e return an empty SVG
    WHERE e.ensembl_transcript_id = ?
                        """, (transcript_id,))
    row2 = cursor.fetchall() # could be multiple expression entries per transcript
    conn.close()
    print(row1.keys())
    print(row2[1].keys())
    return row1, row2 # could name them otherwise

def plot_gene_parts(gene_id):
    """
    Plots the count of transcripts expressed in different atlas organism parts for a given gene ID.
    Args:
        gene_id (str): The Ensembl gene ID to plot expression data for.
    Returns:
        dict: A dictionary mapping atlas organism parts to their respective transcript counts.
    """
    _, _, expression_info = fetch_gene_by_id(gene_id) # we only need expression_info (prevent redundant functions)
    list_of_expression_info = [
        expr['atlas_organism_part'] for expr in expression_info
        if expr['atlas_organism_part'] is not None # filter could be done in SQL query
    ]
    print(list_of_expression_info)
    conn = get_db_connection()
    cursor = conn.cursor()
    if not list_of_expression_info:
        conn.close()
        return {}
    placeholders = ",".join("?" for _ in list_of_expression_info)
    sql = f"""
        SELECT e.atlas_organism_part, COUNT(t.ensembl_transcript_id) as count
        FROM Expression e
        INNER JOIN Transcripts t
        ON e.ensembl_transcript_id = t.ensembl_transcript_id
        WHERE atlas_organism_part IN ({placeholders})
        AND t.ensembl_gene_id = ?
        GROUP BY e.atlas_organism_part
        ORDER BY count DESC
    """
    params = tuple(list_of_expression_info) + (gene_id,)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    rows = {row['atlas_organism_part']: row['count'] for row in rows}
    return rows