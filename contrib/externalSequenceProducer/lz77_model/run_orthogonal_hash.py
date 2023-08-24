import argparse
from file_io import InputReader, SeqWritter
from orthogonal_hash_model import OrthogonalHashModel


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='LazyRowHashLZ77',
                        description='lazy lz77 model')

    parser.add_argument('input_file_path')
    parser.add_argument('output_seq_path')
    args = parser.parse_args()

    input_reader = InputReader(args.input_file_path)
    seq_writter = SeqWritter(args.output_seq_path)

    model = OrthogonalHashModel(input_reader, seq_writter, 
                            window_log=21, 
                            hash_cover_bytes=5, 
                            min_match_len=4,
                            max_match_len=64,
                            hash_log=20,
                            row_log=6,
                            tag_bits=8,
                            nb_attempts=64,
                            bank_log=5,
                            parallel_width=16
                            )
    
    model.process()
    model.print_stat()
    seq_writter.close()
    
    
