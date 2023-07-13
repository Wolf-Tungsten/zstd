import argparse
from file_io import InputReader, SeqWritter
from double_fast_model import DoubleFastModel


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='LZ77Model',
                        description='simple lz77 model')

    parser.add_argument('input_file_path')
    parser.add_argument('output_seq_path')

    args = parser.parse_args()

    input_reader = InputReader(args.input_file_path)
    seq_writter = SeqWritter(args.output_seq_path)

    model = DoubleFastModel(input_reader, seq_writter, 
                            window_log=21, 
                            hash_cover_bytes=8, 
                            large_hash_bits=17, 
                            small_hash_bits=16,
                            min_match_len=5)
    
    model.process()
    seq_writter.close()
    
    
