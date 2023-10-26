#!/usr/bin/env python3

import typer
import csv
from collections import defaultdict

app = typer.Typer()

def validate_gff3(file_path: str) -> bool:
    with open(file_path, 'r') as f:
        for line in f:
            if not line.startswith("#"):
                columns = line.strip().split("\t")
                if len(columns) != 9:
                    return False
    return True

def validate_table(file_path: str) -> bool:
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) != 2:
                return False
    return True

def load_table(file_path: str) -> dict:
    table = {}
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            table[row[0]] = row[1]
    return table

@app.command()
def main(gff3: str = typer.Option(..., "-g", "--gff3", help="Input GFF3 file. You can also put in a GTF file."),
         table: str = typer.Option(..., "-t", "--table", help="Input table file"),
         out: str = typer.Option(..., "-o", "--out", help="Output file")):
    if not validate_gff3(gff3):
        typer.echo("The provided GFF3/GTF file is not valid.")
        raise typer.Exit(code=1)

    if not validate_table(table):
        typer.echo("The provided table file is not valid. It should be a tab-separated file with exactly two columns.")
        raise typer.Exit(code=1)

    mapping_table = load_table(table)

    with open(gff3, 'r') as infile, open(out, 'w') as outfile:
        for line in infile:
            if line.startswith("#"):
                outfile.write(line)
                continue

            columns = line.strip().split("\t")
            id_ = columns[0]

            if id_ in mapping_table:
                columns[0] = mapping_table[id_]

            outfile.write("\t".join(columns) + "\n")

if __name__ == "__main__":
    app()

