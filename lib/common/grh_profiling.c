#include "stdio.h"
long grh_profiling_ml_histogram[2048] = {0};
long grh_profiling_offset_histogram[2048] = {0};
void update_grh_ml_histogram(int ml);
void update_grh_offset_histogram(int offset);
void print_grh_profiling();
void update_grh_ml_histogram(int ml) {
    if (ml < 2047) {
        grh_profiling_ml_histogram[ml]++;
    } else {
        grh_profiling_ml_histogram[2047]++;
    }
}
void update_grh_offset_histogram(int offset) {
    offset >>= 10;
    if (offset < 2047) {
        grh_profiling_offset_histogram[offset]++;
    } else {
        grh_profiling_offset_histogram[2047]++;
    }
}
void print_grh_profiling() {
    for (int i = 0; i < 2048; i++) {
        printf("%d, ML, %ld, OFFSET, %ld\n", i, grh_profiling_ml_histogram[i], grh_profiling_offset_histogram[i]);
    }
}