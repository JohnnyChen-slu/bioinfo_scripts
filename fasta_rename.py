#!/usr/bin/env python3

# Version: 1.0.0
__version__ = "1.0.0"
# revision date: 2023-10-26
__revision_date__ = "2023-10-26"


"""
This script is used for renaming IDs in a FASTA file based on a mapping table.
Usage:
    python script.py -i input.fasta -t table.txt -o output.fasta
"""

import typer
import csv
from collections import defaultdict

app = typer.Typer(add_completion=False, help="A tool for renaming IDs in a FASTA file based on a mapping table.")

def validate_fasta(file_path: str) -> bool:
    """
    Validate if the given file is a FASTA file.
    """
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith(">"):
                return True
    return False

def validate_table(file_path: str) -> bool:
    """
    Validate if the given file is a proper mapping table.
    """
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) != 2:
                return False
    return True

def load_table(file_path: str) -> dict:
    """
    Load the mapping table into a dictionary.
    """
    table = {}
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            table[row[0]] = row[1]
    return table

@app.command()
def main(input: str = typer.Option(..., "-i", "--input", help="Input FASTA file"),
         table: str = typer.Option(..., "-t", "--table", help="Input table file"),
         out: str = typer.Option(..., "-o", "--out", help="Output file")):
    """
    The main function to execute the ID renaming.
    """
    # Validate the input FASTA file
    if not validate_fasta(input):
        typer.echo("Error: The provided FASTA file is not valid.")
        raise typer.Exit(code=1)

    # Validate the mapping table
    if not validate_table(table):
        typer.echo("Error: The provided table file is not valid. It should be a tab-separated file with exactly two columns.")
        raise typer.Exit(code=1)

    # Load the mapping table
    mapping_table = load_table(table)
    multiple_matches = defaultdict(list)

    # Perform the renaming
    with open(input, 'r') as infile, open(out, 'w') as outfile:
        for line in infile:
            if line.startswith(">"):
                id_ = line[1:].strip()
                replacements = [new_id for old_id, new_id in mapping_table.items() if old_id in id_]
                
                if len(replacements) > 1:
                    multiple_matches[id_].extend(replacements)

                elif len(replacements) == 1:
                    outfile.write(">" + replacements[0] + "\n")
                    continue

                else:
                    typer.echo(f"Warning: {id_} does not exist in your provided table file.")
                
                outfile.write(line)
            else:
                outfile.write(line)

    # Check for multiple matches
    if multiple_matches:
        typer.echo("Error: Multiple matches found for the following IDs:")
        for id_, matches in multiple_matches.items():
            typer.echo(f"{id_}: matched with {', '.join(matches)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

