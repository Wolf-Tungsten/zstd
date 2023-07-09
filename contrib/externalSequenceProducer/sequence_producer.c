/*
 * Copyright (c) Yann Collet, Meta Platforms, Inc.
 * All rights reserved.
 *
 * This source code is licensed under both the BSD-style license (found in the
 * LICENSE file in the root directory of this source tree) and the GPLv2 (found
 * in the COPYING file in the root directory of this source tree).
 * You may select, at your option, one of the above-listed licenses.
 */

#include "zstd_compress_internal.h"
#include "sequence_producer.h"
#include "stdio.h"

void getNextSeq(SimpleSimulatorSequenceProducerState* state, ZSTD_Sequence* seq) {
   uint64_t seqBundle = 0;
   fread(&seqBundle, sizeof(uint64_t), 1, state->fd);
   seq->offset = seqBundle & 0x00FFFFFFFF;
   seq->litLength = (seqBundle >> 32) & 0x00FFFF;
   seq->matchLength = (seqBundle >> 48) & 0x00FFFF;
   seq->rep = 0;
}

size_t simpleSimulatorSequenceProducer(
  void* sequenceProducerState,
  ZSTD_Sequence* outSeqs, size_t outSeqsCapacity,
  const void* src, size_t srcSize,
  const void* dict, size_t dictSize,
  int compressionLevel,
  size_t windowSize
) {
    //printf("src=%ld\n", src);
    SimpleSimulatorSequenceProducerState* state = (SimpleSimulatorSequenceProducerState*)sequenceProducerState;
    (void)dict;
    (void)dictSize;
    (void)outSeqsCapacity;
    (void)compressionLevel;


    int encodeLength = 0;
    int seqCount = 0;
    while(1) {
        ZSTD_Sequence seq;
        getNextSeq(state, &seq);
        seq.litLength += state->headLitLen;
        state->headLitLen = 0;
        if(seq.litLength == 0 && seq.matchLength == 0) {
            seq.litLength = srcSize - encodeLength;
            seq.matchLength = 0;
            seq.offset = 0;
            outSeqs[seqCount++] = seq;
            encodeLength += seq.litLength;
            break;
        }
        if(encodeLength + seq.litLength + seq.matchLength > srcSize){
            state->headLitLen = (encodeLength + seq.litLength + seq.matchLength) - srcSize;
            int remainLen = srcSize - encodeLength;
            seq.litLength = remainLen;
            seq.matchLength = 0;
            seq.offset = 0;
            encodeLength += (seq.litLength + seq.matchLength);
            outSeqs[seqCount++] = seq;
            break;
        } else if(encodeLength + seq.litLength + seq.matchLength == srcSize) {
            state->headLitLen = 0;
            seq.litLength += seq.matchLength;
            seq.matchLength = 0;
            seq.offset = 0;
            outSeqs[seqCount++] = seq;
            encodeLength += (seq.litLength + seq.matchLength);
            break;
        }
        encodeLength += (seq.litLength + seq.matchLength);
        outSeqs[seqCount++] = seq;
    }

    if(encodeLength != srcSize) {
        printf("encodeLength=%d, srcSize=%ld\n", encodeLength, srcSize);
    }
    return seqCount;
}