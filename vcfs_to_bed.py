import os
import glob
import gzip

def read_vcf(path: str):
    """Returns a generator to stream the file line by line."""
    if path.endswith('.gz'):
        print(f'\tStreaming {path} (GZ mode)')
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            for line in f:
                yield line
    else:
        print(f'\tStreaming {path}')
        with open(path, 'r') as f:
            for line in f:
                yield line

def get_pop_freqs(info: str, convert_to_minor: bool = True):
    results = []
    fields = info.split(";")
    for i in fields:
        if "_AF=" in i:
            try:
                freq = float(i.split("=")[1])
                if freq > 0.5 and convert_to_minor:
                    freq = 1 - freq
                results.append(freq)
            except (ValueError, IndexError):
                pass 
    return results

def vcf_to_positions(path: str, pop_thresh: float = 0.35, total_thresh: float = 0.25, filter_indel: bool = True):
    print('\tVariants to positions...')
    positions = []
    total_sites = 0
    
    # This now iterates line-by-line without loading the whole file
    for line in read_vcf(path):
        if line.startswith('#'):
            continue
            
        total_sites += 1
        fields = line.strip().split("\t")
        
        if fields[6] not in ['PASS', '.']:
            continue
        if filter_indel and len(fields[3]) != len(fields[4]):
            continue
            
        pop_freqs = get_pop_freqs(fields[7])
        if len(pop_freqs) > 0 and (max(pop_freqs) > pop_thresh or sum(pop_freqs)/len(pop_freqs) > total_thresh):
            positions.append([fields[0], fields[1]])
            
    # Avoid division by zero if the VCF is empty or only headers
    pct = (100 * len(positions) / total_sites) if total_sites > 0 else 0
    print(f'Collected {len(positions)} sites out of {total_sites} ({pct:.1f}%) from {path}.')
    return positions

def positions_to_bed(positions: list, add_chr: bool = True):
    bed_strs = []
    for i in positions:
        chrom = i[0]
        if add_chr and not chrom.startswith('chr'):
            chrom = f'chr{chrom}'
        # BED format is 0-indexed, but VCF is 1-indexed. 
        # Usually, VCF Pos -> BED requires subtracting 1 from the start.
        bed_strs.append(f'{chrom}\t{int(i[1])-1}\t{i[1]}')
    return bed_strs

def multi_vcf_to_bed(dir_path: str, output: str = "combined.bed"):
    inputs = glob.glob(os.path.join(dir_path, '*.vcf')) + glob.glob(os.path.join(dir_path, '*.vcf.gz'))
    inputs.sort()
    print(f'Processing {len(inputs)} files...\n')
    
    with open(output, 'w') as out:
        for i in inputs:
            print(f'Processing: {i}')
            positions = vcf_to_positions(i)
            bed_lines = positions_to_bed(positions)
            for j in bed_lines:
                out.write(j + '\n')
    print('Finished!')

if __name__ == "__main__":
    multi_vcf_to_bed('.')