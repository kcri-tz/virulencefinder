import gzip
import tabulate
def text_table(headers, rows, empty_replace='-'):
    ''' Create text table

    USAGE:
        >>> from tabulate import tabulate
        >>> headers = ['A','B']
        >>> rows = [[1,2],[3,4]]
        >>> print(text_table(headers, rows))
        **********
          A     B
        **********
          1     2
          3     4
        ==========
    '''
    # Replace empty cells with placeholder
    rows = map(lambda row: map(lambda x: x if x else empty_replace, row), rows)
    # Create table
    table = tabulate(rows, headers, tablefmt='simple').split('\n')
    # Prepare title injection
    width = len(table[0])
    # Switch horisontal line
    table[1] = '*' * (width + 2)
    # Update table with title
    table = (("%s\n" * 3)
             % ('*' * (width + 2), '\n'.join(table), '=' * (width + 2)))
    return table


def is_gzipped(file_path):
    ''' Returns True if file is gzipped and False otherwise.
         The result is inferred from the first two bits in the file read
         from the input path.
         On unix systems this should be: 1f 8b
         Theoretically there could be exceptions to this test but it is
         unlikely and impossible if the input files are otherwise expected
         to be encoded in utf-8.
    '''
    with open(file_path, mode='rb') as fh:
        bit_start = fh.read(2)
    if(bit_start == b'\x1f\x8b'):
        return True
    else:
        return False


def get_file_format(input_files):
    """
    Takes all input files and checks their first character to assess
    the file format. Returns one of the following strings; fasta, fastq,
    other or mixed. fasta and fastq indicates that all input files are
    of the same format, either fasta or fastq. other indiates that all
    files are not fasta nor fastq files. mixed indicates that the inputfiles
    are a mix of different file formats.
    """

    # Open all input files and get the first character
    file_format = []
    invalid_files = []
    for infile in input_files:
        if is_gzipped(infile):
            f = gzip.open(infile, "rb")
            fst_char = f.read(1)
        else:
            f = open(infile, "rb")
            fst_char = f.read(1)
        f.close()
        # Assess the first character
        if fst_char == b"@":
            file_format.append("fastq")
        elif fst_char == b">":
            file_format.append("fasta")
        else:
            invalid_files.append("other")
    if len(set(file_format)) != 1:
        return "mixed"
    return ",".join(set(file_format))