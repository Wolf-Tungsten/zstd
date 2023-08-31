
class RowHashTable(object):
    def __init__(self, input_reader, hash_log, row_log, tag_bits, hash_cover_bytes):
        self.input_data = input_reader.read()
        self.hash_table = {}
        self.next_insert_ip = 0
        self.hash_log = hash_log
        self.row_log = row_log
        self.tag_bits = tag_bits
        self.hash_cover_bytes = hash_cover_bytes
        self.row_size = 1 << self.row_log
        self.hash_bits = hash_log - row_log + tag_bits

    def __hash_func(self, raw_bytes, output_bits):
        # concat raw_bytes as a integer
        raw_bytes_int = int.from_bytes(raw_bytes, byteorder='little')
        prime = [0, 0, 0, 506832829, 2654435761, 889523592379, 227718039650203, 58295818150454627, 0xCF1BBCDCB7A56463]
        input_bytes = len(raw_bytes)
        if input_bytes <= 4:
            return ((raw_bytes_int * prime[input_bytes]) & (0xFFFFFFFF)) >> (32 - output_bits)
        else:
            return (((raw_bytes_int << (64-input_bytes*8)) * prime[input_bytes]) & (0xFFFFFFFFFFFFFFFF)) >> (64 - output_bits)
        
    def __row_tag_hash(self, ip):
        original_hash_value = self.__hash_func(
            self.input_data[ip:ip+self.hash_cover_bytes], self.hash_bits)
        tag = original_hash_value & ((1 << self.tag_bits) - 1)
        row = (original_hash_value >> self.tag_bits) & (
            (1 << (self.hash_log - self.row_log)) - 1)
        return row, tag   

    def update_and_read(self, ip):
        # 先进行更新
        while self.next_insert_ip < ip:
            row_idx, tag = self.__row_tag_hash(self.next_insert_ip)
            if row_idx not in self.hash_table:
                self.hash_table[row_idx] = []
            hash_row = self.hash_table[row_idx]
            hash_row.insert(0, (self.next_insert_ip, tag))
            if len(hash_row) > self.row_size:
                hash_row.pop(len(hash_row) - 1)
            self.next_insert_ip += 1
        # 再进行读取
        row_idx, tag = self.__row_tag_hash(ip)
        if row_idx not in self.hash_table:
            return []
        hash_row = self.hash_table[row_idx]
        res = []
        for history_addr, history_tag in hash_row:
            if history_tag == tag:
                res.append(history_addr)
        return res