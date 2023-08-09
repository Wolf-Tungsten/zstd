#include "vtune_itt.h"
#include <stdlib.h>

__itt_domain* vtune_lz77_ratio_domain;
__itt_string_handle* vtune_lz77_task_handle;
__itt_string_handle* vtune_entenc_task_handle;
__itt_string_handle* vtune_compress_block_handle;

void vtune_itt_init(void) {
    vtune_lz77_ratio_domain = __itt_domain_create("lz77_ratio");
    vtune_lz77_task_handle = __itt_string_handle_create("lz77_task");
    vtune_entenc_task_handle = __itt_string_handle_create("entenc_task");
    vtune_compress_block_handle = __itt_string_handle_create("compress_block");
}

void vtune_itt_done(void){
}

void update_dist_histogram(uint64_t offset) {
   
}

void update_match_length_histogram(uint64_t ml){
    
}

