import argparse
from file_io import InputReader, SeqWritter
from lazy_row_hash_model import LazyRowHashModel


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='LazyRowHashLZ77',
                        description='lazy lz77 model')

    parser.add_argument('input_file_path')
    parser.add_argument('output_seq_path')
    args = parser.parse_args()

    input_reader = InputReader(args.input_file_path)
    seq_writter = SeqWritter(args.output_seq_path)

    model = LazyRowHashModel(input_reader, seq_writter, 
                            window_log=21, 
                            hash_cover_bytes=5, 
                            min_match_len=4,
                            hash_log=20,
                            row_log=6,
                            tag_bits=8,
                            nb_attempts=64,
                            lazy_depth=2
                            )
    
    model.process()
    seq_writter.close()
    
    
