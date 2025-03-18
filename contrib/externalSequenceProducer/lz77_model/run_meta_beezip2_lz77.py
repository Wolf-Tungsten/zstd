import argparse
from file_io import InputReader, SeqWritter
from meta_hash_table import MetaHashTable
from beezip2_lz77_model import BeeZip2LZ77Model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='Meta BeeZip2 LZ77',
                        description='lazy lz77 model')

    parser.add_argument('input_file_path')
    parser.add_argument('output_seq_path')
    args = parser.parse_args()

    input_reader = InputReader(args.input_file_path)
    seq_writter = SeqWritter(args.output_seq_path)

    hash_table = MetaHashTable(input_reader,
                                window_log=22,
                                hash_log=16,
                                row_log=4,
                                hash_cover_bytes=5,
                                parallel_width=16,
                                bank_log=5,
                                min_match_len=4,
                                meta_len=15,
                                hqt=4)
    lz77_model = BeeZip2LZ77Model(input_reader, seq_writter, hash_table,
                            window_log=16, 
                            min_match_len=4,
                            hash_cover_bytes=5,
                            lazy_len=4,
                            meta_len=15
                            )
    
    lz77_model.process()
    seq_writter.close()
    
    
