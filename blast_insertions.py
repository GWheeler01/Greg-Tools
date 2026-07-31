from Bio.Blast import NCBIWWW, NCBIXML

def ncbi_blast(sequence_data: str):
    # Submit sequence string to BLASTN searching against the nucleotide database ('nt')
    result_handle = NCBIWWW.qblast(
        program="blastn",
        database="nt",
        sequence=sequence_data,
        hitlist_size=20,
        expect=1.0,
        megablast=True
    )
    
    # Parse the resulting XML
    blast_records = NCBIXML.parse(result_handle)
    return blast_records

def parse_records(blast_records):
    for record in blast_records:
        for alignment in record.alignments:
            for hsp in alignment.hsps:
                return {"Sequence":alignment.title, "Length":alignment.length, "E-value": hsp.expect, "Identities":hsp.identities}
    return {}

import sys, gzip, json, time

input_file = sys.argv[1]

if len(sys.argv) < 3:
    output_file = "blast_results.txt"
else:
    output_file = sys.argv[2]

if len(sys.argv) < 4:
    sleep_delay = 5
else:
    sleep_delay = float(sys.argv[3])

if input_file.endswith('gz'):
    with gzip.open(input_file, 'rt') as handle:
        data_lines = handle.readlines()
else:
    with open(input_file, 'r') as handle:
        data_lines = handle.readlines()

with open(output_file, 'w', buffering=1) as out:
    count = 0
    out.write("{")
    for i in data_lines:
        if i.startswith('#'):
            continue
        if "SVTYPE=INS" in i:
            fields = i.strip().split()
            id = f"{fields[0]}:{fields[1]}"
            seq = fields[4]
            print(f'{count} : {seq}')
            success = False
            retries = 0
            while success is False and retries < 20:
                try:
                    record = ncbi_blast(seq)
                    record_dict = parse_records(record)
                    print(record_dict)
                    out.write(f'\"{id}\":{json.dumps(record_dict)},\n')
                    success = True
                    time.sleep(sleep_delay)
                except Exception as e:
                    print(f'Error: {str(e)}')
                    retries += 1
                    time.sleep(sleep_delay * 2)
            count += 1
    out.write("}")
