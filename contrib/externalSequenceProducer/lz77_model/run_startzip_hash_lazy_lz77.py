import argparse
from file_io import InputReader, SeqWritter
from starzip_hash_table import StarzipHashTable
from lazy_lz77_model import LazyLZ77Model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='StarzipHashLZ77',
                        description='lazy lz77 model')

    parser.add_argument('input_file_path')
    parser.add_argument('output_seq_path')
    args = parser.parse_args()

    input_reader = InputReader(args.input_file_path)
    seq_writter = SeqWritter(args.output_seq_path)

    hash_table = StarzipHashTable(input_reader,
                              hash_log=20,
                              row_log=4,
                              tag_bits=8,
                              hash_cover_bytes=5,
                              parallel_width=16,
                              bank_num=32)
    lz77_model = LazyLZ77Model(input_reader, seq_writter, hash_table,
                            window_log=21, 
                            min_match_len=4,
                            nb_attempts=16,
                            hash_cover_bytes=4
                            )
    
    lz77_model.process()
    seq_writter.close()
    
    
