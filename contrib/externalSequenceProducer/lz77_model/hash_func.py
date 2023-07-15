# static const U32 prime4bytes = 2654435761U;
# static U32    ZSTD_hash4(U32 u, U32 h) { assert(h <= 32); return (u * prime4bytes) >> (32-h) ; }
# static size_t ZSTD_hash4Ptr(const void* ptr, U32 h) { return ZSTD_hash4(MEM_readLE32(ptr), h); }

# static const U64 prime5bytes = 889523592379ULL;
# static size_t ZSTD_hash5(U64 u, U32 h) { assert(h <= 64); return (size_t)(((u  << (64-40)) * prime5bytes) >> (64-h)) ; }
# static size_t ZSTD_hash5Ptr(const void* p, U32 h) { return ZSTD_hash5(MEM_readLE64(p), h); }

# static const U64 prime6bytes = 227718039650203ULL;
# static size_t ZSTD_hash6(U64 u, U32 h) { assert(h <= 64); return (size_t)(((u  << (64-48)) * prime6bytes) >> (64-h)) ; }
# static size_t ZSTD_hash6Ptr(const void* p, U32 h) { return ZSTD_hash6(MEM_readLE64(p), h); }

# static const U64 prime7bytes = 58295818150454627ULL;
# static size_t ZSTD_hash7(U64 u, U32 h) { assert(h <= 64); return (size_t)(((u  << (64-56)) * prime7bytes) >> (64-h)) ; }
# static size_t ZSTD_hash7Ptr(const void* p, U32 h) { return ZSTD_hash7(MEM_readLE64(p), h); }

# static const U64 prime8bytes = 0xCF1BBCDCB7A56463ULL;
# static size_t ZSTD_hash8(U64 u, U32 h) { assert(h <= 64); return (size_t)(((u) * prime8bytes) >> (64-h)) ; }
# static size_t ZSTD_hash8Ptr(const void* p, U32 h) { return ZSTD_hash8(MEM_readLE64(p), h); }

def hash_func(raw_bytes, output_bits):
    # concat raw_bytes as a integer
    raw_bytes_int = int.from_bytes(raw_bytes, byteorder='little')
    prime = [0, 0, 0, 506832829, 2654435761, 889523592379, 227718039650203, 58295818150454627, 0xCF1BBCDCB7A56463]
    input_bytes = len(raw_bytes)
    if input_bytes <= 4:
        return ((raw_bytes_int * prime[input_bytes]) & (0xFFFFFFFF)) >> (32 - output_bits)
    else:
        return (((raw_bytes_int << (64-input_bytes*8)) * prime[input_bytes]) & (0xFFFFFFFFFFFFFFFF)) >> (64 - output_bits)


