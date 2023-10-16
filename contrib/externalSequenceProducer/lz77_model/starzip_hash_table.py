from row_hash_table import RowHashTable

class StarzipHashTable(RowHashTable):
    def __init__(self, input_reader, hash_log, row_log, tag_bits, hash_cover_bytes, parallel_width, bank_num):
        RowHashTable.__init__(self, input_reader, hash_log, row_log, tag_bits, hash_cover_bytes)
        self.parallel_width = parallel_width
        self.bank_num = bank_num
        self.conflict_book = {}


    def update_and_read(self, ip):
        # 先进行更新
        while self.next_insert_ip < ip:
            row_idx, tag = self.row_tag_hash(self.next_insert_ip)
            if row_idx not in self.hash_table:
                self.hash_table[row_idx] = [[False, 0, 0] for _ in range(self.row_size)]
            hash_row = self.hash_table[row_idx]
            col_idx = self.next_insert_ip % self.row_size
            hash_row[col_idx] = [True, self.next_insert_ip, tag]
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
        for valid, history_addr, history_tag in hash_row:
            if valid and history_tag == tag:
                res.append(history_addr)
        return res