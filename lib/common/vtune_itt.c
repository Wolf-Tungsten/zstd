#include "vtune_itt.h"
#include <stdlib.h>

__itt_domain* vtune_dist_histogram_domain;
__itt_string_handle* vtune_dist_histogram_handle;
int max_dist_kb = 2048;
uint64_t* vtune_dist_histogram_x;
uint64_t* vtune_dist_histogram_y;
uint64_t seq_count;
uint64_t vtune_dist_histogram_seg_x[6] = {1, 32, 64, 512, 1024, 2048};
uint64_t vtune_dist_histogram_seg_y[6] = {0, 0, 0, 0, 0, 0};
double vtune_dist_histogram_seg_ratio_y[5];
__itt_domain* vtune_match_length_histogram_domain;
int max_match_length = 2048;
uint64_t* vtune_match_length_histogram_x;
uint64_t* vtune_match_length_histogram_y;
uint64_t vtune_match_length_histogram_seg_x[3] = {16, 32, 47};
uint64_t vtune_match_length_histogram_seg_y[3] = {0, 0, 0};
double vtune_match_length_histogram_seg_ratio_y[3];

void vtune_itt_init(void) {
    vtune_dist_histogram_domain = __itt_domain_create("dist_histogram_domain");
    // vtune_dist_histogram_handle = __itt_string_handle_create("dist_histogram");
    vtune_dist_histogram_x = malloc(sizeof(uint64_t) * (max_dist_kb + 1));
    vtune_dist_histogram_y = malloc(sizeof(uint64_t) * (max_dist_kb + 1));
    for(int i = 0; i < max_dist_kb + 1; i++){
        vtune_dist_histogram_x[i] = i;
        vtune_dist_histogram_y[i] = 0;
    }
    seq_count = 0;
    vtune_match_length_histogram_domain = __itt_domain_create("match_length_histogram_domain");
    vtune_match_length_histogram_x = malloc(sizeof(uint64_t) * (max_match_length+2));
    vtune_match_length_histogram_y = malloc(sizeof(uint64_t) * (max_match_length+2)); 
    for(int i = 0; i < max_match_length + 2; i++){
        vtune_match_length_histogram_x[i] = i;
        vtune_match_length_histogram_y[i] = 0;
    }
}

void vtune_itt_done(void){
    __itt_histogram* dist_histogram = __itt_histogram_create(vtune_dist_histogram_domain, "dist_histogram", __itt_metadata_u64, __itt_metadata_u64);
    __itt_histogram_submit(dist_histogram, max_dist_kb+1, vtune_dist_histogram_x, vtune_dist_histogram_y);
    free(vtune_dist_histogram_x);
    free(vtune_dist_histogram_y);
    __itt_histogram* dist_histogram_seg = __itt_histogram_create(vtune_dist_histogram_domain, "dist_histogram_seg", __itt_metadata_u64, __itt_metadata_u64);
    __itt_histogram_submit(dist_histogram_seg, 6, vtune_dist_histogram_seg_x, vtune_dist_histogram_seg_y);
    for(int i=0; i<6; i++){
        vtune_dist_histogram_seg_ratio_y[i] = ((double)vtune_dist_histogram_seg_y[i]) / seq_count * 100 * 1000;
    }
    __itt_histogram* dist_histogram_seg_ratio = __itt_histogram_create(vtune_dist_histogram_domain, "dist_histogram_ratio", __itt_metadata_u64, __itt_metadata_double);
    __itt_histogram_submit(dist_histogram_seg_ratio, 6, vtune_dist_histogram_seg_x, vtune_dist_histogram_seg_ratio_y);

    __itt_histogram* match_length_histogram = __itt_histogram_create(vtune_match_length_histogram_domain, "match_length_histogram", __itt_metadata_u64, __itt_metadata_u64);
    __itt_histogram_submit(match_length_histogram, max_match_length+2, vtune_match_length_histogram_x, vtune_match_length_histogram_y);
    free(vtune_match_length_histogram_x);
    free(vtune_match_length_histogram_y);
    __itt_histogram* match_length_histogram_seg = __itt_histogram_create(vtune_match_length_histogram_domain, "match_length_histogram_seg", __itt_metadata_u64, __itt_metadata_u64);
    __itt_histogram_submit(match_length_histogram_seg, 3, vtune_match_length_histogram_seg_x, vtune_match_length_histogram_seg_y);
    for(int i=0; i<3; i++){
        vtune_match_length_histogram_seg_ratio_y[i] = ((double)vtune_match_length_histogram_seg_y[i]) / seq_count * 100 * 1000;
    }
    __itt_histogram* match_length_histogram_seg_ratio = __itt_histogram_create(vtune_match_length_histogram_domain, "match_length_histogram_ratio", __itt_metadata_u64, __itt_metadata_double);
    __itt_histogram_submit(match_length_histogram_seg_ratio, 3, vtune_match_length_histogram_seg_x, vtune_match_length_histogram_seg_ratio_y);
}

void update_dist_histogram(uint64_t offset) {
    if(offset >> 10 < vtune_dist_histogram_seg_x[0]){
        vtune_dist_histogram_seg_y[0]++;
    } else if(offset >> 10 < vtune_dist_histogram_seg_x[1]){
        vtune_dist_histogram_seg_y[1]++;
    } else if(offset >> 10 < vtune_dist_histogram_seg_x[2]){
        vtune_dist_histogram_seg_y[2]++;
    } else if(offset >> 10 < vtune_dist_histogram_seg_x[3]){
        vtune_dist_histogram_seg_y[3]++;
    } else if(offset >> 10 < vtune_dist_histogram_seg_x[4]){
        vtune_dist_histogram_seg_y[4]++;
    } else {
        vtune_dist_histogram_seg_y[5]++;
    }
    

    if(offset < max_dist_kb << 10){
        vtune_dist_histogram_y[offset >> 10]++;
    }
}

void update_match_length_histogram(uint64_t ml){
    seq_count += 1;
    if(ml <= max_match_length){
        vtune_match_length_histogram_y[ml] += 1;
    } else {
        vtune_match_length_histogram_y[max_match_length+1] += 1;
    }

    if(ml <= vtune_match_length_histogram_seg_x[0]){
        vtune_match_length_histogram_seg_y[0] += 1;
    } else if(ml <= vtune_match_length_histogram_seg_x[1]) {
        vtune_match_length_histogram_seg_y[1] += 1;
    } else {
        vtune_match_length_histogram_seg_y[2] += 1;
    }
}

