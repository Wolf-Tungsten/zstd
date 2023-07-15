import argparse
from file_io import InputReader, SeqWritter
from row_hash_model import RowHashModel


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='RowHashLZ77',
                        description='simple lz77 model')

    parser.add_argument('input_file_path')
    parser.add_argument('output_seq_path')
    args = parser.parse_args()

    input_reader = InputReader(args.input_file_path)
    seq_writter = SeqWritter(args.output_seq_path)

    model = RowHashModel(input_reader, seq_writter, 
                            window_log=19, 
                            hash_cover_bytes=5, 
                            min_match_len=4,
                            hash_log=20,
                            row_log=1,
                            tag_bits=8,
                            nb_attempts=2
                            )
    
    model.process()
    seq_writter.close()
    
    
