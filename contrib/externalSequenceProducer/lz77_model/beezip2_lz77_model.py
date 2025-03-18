import tqdm
from seq_checker import SeqChecker

class BeeZip2LZ77Model(object):
    def __init__(self, input_reader, seq_writter, hash_table, window_log, min_match_len, hash_cover_bytes, lazy_len, meta_len):
        self.input_reader = input_reader
        self.seq_writter = seq_writter
        self.window_size = 1 << window_log
        self.min_match_len = min_match_len
        self.hash_cover_bytes = hash_cover_bytes
        self.hash_table = hash_table
        self.lazy_len = lazy_len
        self.meta_len = meta_len

        self.input_data = self.input_reader.read()
        self.input_length = len(self.input_data)
        self.ilimit = self.input_length - self.meta_len

        self.next_encode_ip = 0
        self.lazy_count = 0
        self.lazy_res_list = []

        self.seq_checker = SeqChecker(self.input_data)
    
    def count_match_length(self, ip, history_addr):
        match_length = 0
        while match_length <= 1024 and ip + match_length < self.input_length and self.input_data[ip + match_length] == self.input_data[history_addr + match_length] :
            match_length += 1
        return match_length
    
    def lazy_summary(self):
        # 先把每一行的多个结果按照 meta_len 和 offset 选出最长最近的
        lazy_row_res_list = []
        for res in self.lazy_res_list:
            ip, hash_res = res
            if len(hash_res) == 0:
                lazy_row_res_list.append((ip, False, 0, 0))
            else:
                best_offset = ip - hash_res[0][0]
                best_meta_match_len = hash_res[0][1]
                for history_ptr, meta_match_len in hash_res:
                    if meta_match_len > best_meta_match_len:
                        best_meta_match_len = meta_match_len
                        best_offset = ip - history_ptr
                    elif meta_match_len == best_meta_match_len and ip - history_ptr < best_offset:
                        best_offset = ip - history_ptr
                lazy_row_res_list.append((ip, True, best_offset, best_meta_match_len))
        # 选出的结果进行扩展
        ext_res_list = []
        for res in lazy_row_res_list:
            ip, is_match, offset, meta_match_len = res
            if is_match:
                if offset < self.window_size and meta_match_len >= self.meta_len:
                    match_len = self.count_match_length(ip, ip - offset)
                    ext_res_list.append((ip, True, offset, match_len))
                else:
                    ext_res_list.append((ip, True, offset, meta_match_len))
            else:
                ext_res_list.append((ip, False, 0, 0))
        # 计算 gain
        gain_list = []
        for res in ext_res_list:
            ip, is_match, offset, match_len = res
            lit_len = ip - self.next_encode_ip
            offset_bit_count = len(bin(offset)) - 2
            gain = match_len * 4 - offset_bit_count - lit_len * 4
            gain_list.append((ip, lit_len, match_len, offset, gain))
        # 选择最大 gain
        best_match = gain_list[0]
        for res in gain_list:
            if res[4] > best_match[4]:
                best_match = res
        # 输出
        #self.seq_writter.write_seq(offset, enhanced_ip - self.next_encode_ip, match_length)
        self.seq_checker.check(best_match[3], best_match[1], best_match[2])
        self.seq_writter.write_seq(best_match[3], best_match[1], best_match[2])
        self.next_encode_ip += best_match[1] + best_match[2]
        self.lazy_count = 0
        self.lazy_res_list = []


    
    def process(self):
        with tqdm.tqdm(total=self.ilimit) as pbar:
            for ip in range(self.ilimit):
                pbar.update(1)
                hash_res = self.hash_table.update_and_read(ip)
                if ip >= self.next_encode_ip:
                    if self.lazy_count == 0 and len(hash_res) == 0:
                        pass
                    elif self.lazy_count < self.lazy_len:
                        self.lazy_count += 1
                        self.lazy_res_list.append((ip, hash_res))
                    else:
                        self.lazy_summary()
                    
