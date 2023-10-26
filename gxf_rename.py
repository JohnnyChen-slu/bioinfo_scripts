#!/usr/bin/env python3

# Version and Revision date
__version__ = "1.0.1"
__revision_date__ = "2023-10-26"



This script is used for renaming IDs in a GFF3 or GTF file based on a mapping table.
Usage:
    python gxf_rename.py -i input.gff3 -t table.txt -o output.gff3

import typer
import csv
from collections import defaultdict
import logging

app = typer.Typer(add_completion=False, help="A tool for renaming IDs in a GFF3 or GTF file based on a mapping table.")

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def validate_gxf(file_path: str) -> bool:
    "Validate if the given file is a GFF3 or GTF file."
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith("#"):
                continue  # Skip comment lines
            columns = line.strip().split("	")
            if len(columns) >= 8:
                return True
    return False

def validate_table(file_path: str) -> bool:
    "Validate if the given file is a proper mapping table."
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) != 2:
                return False
    return True

def load_table(file_path: str) -> dict:
    "Load the mapping table into a dictionary."
    table = {}
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            table[row[0]] = row[1]
    return table

@app.command()
def main(input: str = typer.Option(..., "-i", "--input", help="Input GFF3 or GTF file"),
         table: str = typer.Option(..., "-t", "--table", help="Input table file"),
         out: str = typer.Option(..., "-o", "--out", help="Output file")):
    "The main function to execute the ID renaming."
    setup_logging()
    # Validate the input GFF3 or GTF file
    if not validate_gxf(input):
        logging.error("The provided GFF3 or GTF file is not valid.")
        raise typer.Exit(code=1)

    # Validate the mapping table
    if not validate_table(table):
        logging.error("The provided table file is not valid. It should be a tab-separated file with exactly two columns.")
        raise typer.Exit(code=1)

    # Load the mapping table
    mapping_table = load_table(table)
    multiple_matches = defaultdict(list)

    # Perform the renaming
    with open(input, 'r') as infile, open(out, 'w') as outfile:
        for line in infile:
            if line.startswith("#"):
                outfile.write(line)
                continue  # Skip comment lines

            columns = line.strip().split("\t")
            if len(columns) < 8:
                logging.warning(f"Skipping malformed line: {line.strip()}")
                continue

            id_ = columns[8]
            replacements = [new_id for old_id, new_id in mapping_table.items() if old_id in id_]
            
            if len(replacements) > 1:
                multiple_matches[id_].extend(replacements)

            elif len(replacements) == 1:
                columns[8] = replacements[0]
                outfile.write("\t".join(columns) + "\n")
                continue

            else:
                logging.warning(f"{id_} does not exist in your provided table file.")
            
            outfile.write(line)

    # Check for multiple matches
    if multiple_matches:
        logging.error("Multiple matches found for the following IDs:")
        for id_, matches in multiple_matches.items():
            logging.error(f"{id_}: matched with {', '.join(matches)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
