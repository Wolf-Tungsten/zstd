from row_hash_table import RowHashTable

class ParallelRowHashTable(RowHashTable):
    def __init__(self, input_reader, hash_log, row_log, tag_bits, hash_cover_bytes, parallel_width, bank_num):
        RowHashTable.__init__(self, input_reader, hash_log, row_log, tag_bits, hash_cover_bytes)
        self.parallel_width = parallel_width
        self.bank_num = bank_num
        self.conflict_book = {}


    def update_and_read(self, ip):
        # 先进行更新
        while self.next_insert_ip < ip:
            if self.next_insert_ip % self.parallel_width == 0:
                self.conflict_book = {}
            row_idx, tag = self.row_tag_hash(self.next_insert_ip)
            bank_idx = row_idx % self.bank_num
            if bank_idx not in self.conflict_book:
                self.conflict_book[bank_idx] = ip
            elif self.conflict_book[bank_idx] == ip:
                pass
            else:
                self.next_insert_ip += 1
                continue
            if row_idx not in self.hash_table:
                self.hash_table[row_idx] = []
            hash_row = self.hash_table[row_idx]
            hash_row.insert(0, (self.next_insert_ip, tag))
            if len(hash_row) > self.row_size:
                hash_row.pop(len(hash_row) - 1)
            self.next_insert_ip += 1
        # 再进行读取
        if ip % self.parallel_width == 0:
            self.conflict_book = {}
        row_idx, tag = self.row_tag_hash(ip)
        bank_idx = row_idx % self.bank_num
        if bank_idx not in self.conflict_book:
            self.conflict_book[bank_idx] = ip
        elif self.conflict_book[bank_idx] == ip:
            pass
        else:
            return []
        if row_idx not in self.hash_table:
            return []
        hash_row = self.hash_table[row_idx]
        res = []
        for history_addr, history_tag in hash_row:
            if history_tag == tag:
                res.append(history_addr)
        return res