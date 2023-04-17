#include "ittnotify.h"

__itt_domain* itt_domain_compressBlock;
__itt_string_handle* itt_handle_block;
__itt_string_handle* itt_handle_lz77;
__itt_string_handle* itt_handle_entropy;

__itt_domain* itt_domain_lz77Histogram;

#define VTUNE_MAX_WLOG 23
#define VTUNE_MAX_MATCH_LENGTH 131074

uint32_t vtune_dist_histogram_x[1 << (VTUNE_MAX_WLOG - 10)];
uint32_t vtune_dist_histogram[1 << (VTUNE_MAX_WLOG - 10)];
uint32_t vtune_match_length_histogram_x[VTUNE_MAX_MATCH_LENGTH];
uint32_t vtune_match_length_histogram[VTUNE_MAX_MATCH_LENGTH];
uint32_t vtune_max_distKB = 0;
uint32_t vtune_max_match_length = 0;

void vtune_itt_init(void)
{
    itt_domain_compressBlock = __itt_domain_create("compressBlock");
    itt_domain_compressBlock ->flags = 0;
    itt_handle_block = __itt_string_handle_create("block");
    itt_handle_lz77 = __itt_string_handle_create("lz77");
    itt_handle_entropy = __itt_string_handle_create("entropy");

    itt_domain_lz77Histogram = __itt_domain_create("lz77Histogram");
    for(int i = 0; i < VTUNE_MAX_MATCH_LENGTH; i++){
        vtune_match_length_histogram_x[i] = i;
        vtune_match_length_histogram[i] = 0;
    }
    for(int i = 0; i < (1 << (VTUNE_MAX_WLOG - 10)); i++){
        vtune_dist_histogram_x[i] = i << 10;
        vtune_dist_histogram[i] = 0;
    }
}

void vtune_update_dist_histogram(uint32_t dist)
{
    uint32_t distKB = dist >> 10;
    if (distKB > vtune_max_distKB) {
        vtune_max_distKB = distKB;
    }
    vtune_dist_histogram[distKB]++;
}

void vtune_update_match_length_histogram(uint32_t match_length)
{
    if (match_length > vtune_max_match_length) {
        vtune_max_match_length = match_length;
    }
    vtune_match_length_histogram[match_length]++;
}

void vtune_itt_finalize(void)
{
    // printf("[Dist Histogram] max_distKB = %d]\n", vtune_max_distKB);
    // for(uint32_t i = 0; i < vtune_max_distKB + 1; i++){
    //     printf("%d,%d\n", i, vtune_dist_histogram[i]);
    // }
    printf("[Match Length Histogram] max_match_length = %d]\n", vtune_max_match_length);
    for(uint32_t i = 0; i < vtune_max_match_length + 1; i++){
        printf("%d,%d\n", i, vtune_match_length_histogram[i]);
    }
    // __itt_histogram* itt_dist_histogram = __itt_histogram_create(itt_domain_lz77Histogram, "dist", __itt_metadata_u32, __itt_metadata_u64);
    // __itt_histogram* itt_match_length_histogram = __itt_histogram_create(itt_domain_lz77Histogram, "match_length", __itt_metadata_u32, __itt_metadata_u64);
    // __itt_histogram_submit(itt_dist_histogram, vtune_max_distKB, vtune_dist_histogram_x, vtune_dist_histogram);
    // __itt_histogram_submit(itt_match_length_histogram, vtune_max_match_length, vtune_match_length_histogram_x, vtune_match_length_histogram);
}