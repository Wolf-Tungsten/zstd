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

#define HSIZE 1024
static U32 const HLOG = 10;
static U32 const MLS = 4;
static U32 const BADIDX = 0xffffffff;
SimulatorState ss;

size_t simpleSequenceProducer(
  void* sequenceProducerState,
  ZSTD_Sequence* outSeqs, size_t outSeqsCapacity,
  const void* src, size_t srcSize,
  const void* dict, size_t dictSize,
  int compressionLevel,
  size_t windowSize
) {
    const BYTE* const istart = (const BYTE*)src;
    const BYTE* const iend = istart + srcSize;
    const BYTE* ip = istart;
    const BYTE* anchor = istart;
    size_t seqCount = 0;
    U32 hashTable[HSIZE];

    (void)sequenceProducerState;
    (void)dict;
    (void)dictSize;
    (void)outSeqsCapacity;
    (void)compressionLevel;

    {   int i;
        for (i=0; i < HSIZE; i++) {
            hashTable[i] = BADIDX;
    }   }

    while (ip + MLS < iend) {
        size_t const hash = ZSTD_hashPtr(ip, HLOG, MLS);
        U32 const matchIndex = hashTable[hash];
        hashTable[hash] = (U32)(ip - istart);

        if (matchIndex != BADIDX) {
            const BYTE* const match = istart + matchIndex;
            U32 const matchLen = (U32)ZSTD_count(ip, match, iend);
            if (matchLen >= ZSTD_MINMATCH_MIN) {
                U32 const litLen = (U32)(ip - anchor);
                U32 const offset = (U32)(ip - match);
                ZSTD_Sequence const seq = {
                    offset, litLen, matchLen, 0
                };

                /* Note: it's crucial to stay within the window size! */
                if (offset <= windowSize) {
                    outSeqs[seqCount++] = seq;
                    ip += matchLen;
                    anchor = ip;
                    continue;
                }
            }
        }

        ip++;
    }

    {   ZSTD_Sequence const finalSeq = {
            0, (U32)(iend - anchor), 0, 0
        };
        outSeqs[seqCount++] = finalSeq;
    }

    return seqCount;
}


void loadSeqAndIndexFile(const char* srcFilePath){
  char filepath[1024];

  // load seq file
  sprintf(filepath, "%s.seq", srcFilePath);
  FILE* f = fopen(filepath, "rb");
  if (f == NULL) {
    printf("Error: cannot open file %s\n", filepath);
    exit(1);
  }
  fseek(f, 0, SEEK_END);
  size_t fsize = ftell(f);
  fseek(f, 0, SEEK_SET);
  ss.seqBuffer = (uint64_t*)malloc(fsize);
  ss.seqAmount = fsize / sizeof(uint64_t);
  fread(ss.seqBuffer, sizeof(uint64_t), ss.seqAmount, f);
  fclose(f);

  // load index file
  sprintf(filepath, "%s.index", srcFilePath);
  f = fopen(filepath, "rb");
  if (f == NULL) {
    printf("Error: cannot open file %s\n", filepath);
    exit(1);
  }
  fseek(f, 0, SEEK_END);
  fsize = ftell(f);
  fseek(f, 0, SEEK_SET);
  ss.indexBuffer = (uint64_t*)malloc(fsize);
  ss.indexAmount = fsize / sizeof(uint64_t);
  fread(ss.indexBuffer, sizeof(uint64_t), ss.indexAmount, f);
  fclose(f);
}

void getIndexAtPos(size_t pos, SimulatorIndex* index){
  uint64_t indexValue = ss.indexBuffer[pos];
  index->prevSeqAmount = indexValue & 0x0ffffffff;
  index->encodeLength = (indexValue >> 32) & 0x0ffffff;
  index->eof = (indexValue >> 56) & 0x01;
}

void getSeqAtPos(size_t pos, ZSTD_Sequence* seq){
  uint64_t seqValue = ss.seqBuffer[pos];
  seq->rep = seqValue & 0x0ff;
  seq->matchLength = (seqValue >> 8) & 0x0ff;
  seq->litLength = (seqValue >> 16) & 0x0ffff;
  seq->offset = (seqValue >> 32) & 0x0ffffffff;
  //printf("matchLength=%d, litLength=%d\n", seq->matchLength, seq->litLength);
}

size_t simulatorSequenceProducer(
  void* sequenceProducerState,
  ZSTD_Sequence* outSeqs, size_t outSeqsCapacity,
  const void* src, size_t srcSize,
  const void* dict, size_t dictSize,
  int compressionLevel,
  size_t windowSize
) {
    (void)sequenceProducerState;
    (void)dict;
    (void)dictSize;
    (void)outSeqsCapacity;
    (void)compressionLevel;

    printf("prevBlockStartPtr: %p, prevBlockSize: %zu, src: %p, srcSize: %zu\n\r", ss.prevBlockStartPtr, ss.prevBlockSize, src, srcSize);
    if(!ss.isFirstBlock) {
        assert(ss.prevBlockStartPtr + ss.prevBlockSize == src);
    } else {
        ss.isFirstBlock = 0;
        ss.firstBlockStartPtr = src;
    }

    if(ss.prevBlockSize > srcSize) {
        printf("last block");
    }

    ss.prevBlockStartPtr = src;
    ss.prevBlockSize = srcSize;

    
    size_t seqCount = 0;
    size_t encodeLength = 0;

    size_t indexPos = (src - ss.firstBlockStartPtr) >> SIMULATOR_SLICE_LOG;
    size_t indexCount = srcSize >> SIMULATOR_SLICE_LOG;
    if(indexPos >= ss.indexAmount) {
        printf("Warning: indexPos > ss.indexAmount, this block will output as all literal\n");
        ZSTD_Sequence const finalSeq = {
            0, (U32)(srcSize), 0, 0
        };
        outSeqs[seqCount++] = finalSeq;
        return seqCount;
    }

    SimulatorIndex index, nextIndex;
    getIndexAtPos(indexPos, &index);
    ZSTD_Sequence seq;
    int concatLitLen = 0;
    for(size_t i = indexPos; i < indexPos + indexCount; i++){
        if(i > ss.indexAmount) {
            // no enough slice, output remain as literal
            assert(encodeLength < srcSize);
            ZSTD_Sequence const finalSeq = {
                0, (U32)(srcSize - encodeLength), 0, 0
            };
            outSeqs[seqCount++] = finalSeq;
            return seqCount;
        }
        int debugSliceEncodeLength = 0;
        // get next index
        getIndexAtPos(i + 1, &nextIndex);
        // size_t sliceSeqAmount = nextIndex.prevSeqAmount - index.prevSeqAmount;
        // assert(index.encodeLength <= SIMULATOR_SLICE_SIZE);
        if(index.encodeLength == 0) {
            if(i == (indexPos + indexCount - 1)) {
                // its a last empty slice
                assert(index.encodeLength == 0);
                ZSTD_Sequence const finalSeq = {
                    0, (U32)(concatLitLen + SIMULATOR_SLICE_SIZE), 0, 0
                };
                outSeqs[seqCount++] = finalSeq;
                return seqCount;
            }
        } else {
            getSeqAtPos(index.prevSeqAmount, &seq);
            debugSliceEncodeLength += (seq.litLength + seq.matchLength);
            seq.litLength += concatLitLen;
            concatLitLen = 0;
            outSeqs[seqCount++] = seq;
            for(size_t j = index.prevSeqAmount + 1; j < nextIndex.prevSeqAmount; j++){
                getSeqAtPos(j, &outSeqs[seqCount++]);
                debugSliceEncodeLength += (outSeqs[seqCount-1].litLength + outSeqs[seqCount-1].matchLength);
            }
            if(debugSliceEncodeLength != index.encodeLength){
                printf("debug here");
            }
            assert(debugSliceEncodeLength == index.encodeLength);
        }
        
        if(i == (indexPos + indexCount - 1)) {
            // last slice
            encodeLength += index.encodeLength;
            if(encodeLength < srcSize) {
                // we need to output remain as literal and mark this block end
                ZSTD_Sequence const finalSeq = {
                    0, (U32)(srcSize - encodeLength), 0, 0
                };
                outSeqs[seqCount++] = finalSeq;
                return seqCount;
            } else {
                // ooops! the last slice is too long, we need to trim it
                int overlapLen = encodeLength - srcSize;
                while(overlapLen >= 0) {
                    seqCount--;
                    if(outSeqs[seqCount].matchLength > overlapLen) {
                        // trim the last seq's matchLength, add remain match length to litLength
                        outSeqs[seqCount].matchLength -= overlapLen;
                        outSeqs[seqCount].litLength += outSeqs[seqCount].matchLength; 
                        // mark the block's end
                        outSeqs[seqCount].matchLength = 0;
                        outSeqs[seqCount].offset = 0;
                        outSeqs[seqCount].rep = 0;
                        seqCount++;
                        break;
                    } else if (outSeqs[seqCount].litLength + outSeqs[seqCount].matchLength > overlapLen) {
                        // trim the last match's matchLength and litLength
                        outSeqs[seqCount].litLength -= (overlapLen - outSeqs[seqCount].matchLength);
                        // mark the block's end
                        outSeqs[seqCount].matchLength = 0;
                        outSeqs[seqCount].offset = 0;
                        outSeqs[seqCount].rep = 0;
                        seqCount++;
                        break;
                    } else {
                        // we need drop the last seq
                        // here is a boundary situation, if the overlap length equal to the last seq's litLength + matchLength
                        // we just left it as 0, as the loop condition allows overlap == 0
                        // it will trim the prev seq and turn it into a block end.
                        overlapLen -= outSeqs[seqCount].litLength + outSeqs[seqCount].matchLength;
                    }
                }
            }
        } else {
            // not last slice
            encodeLength += SIMULATOR_SLICE_SIZE; 
            // we promise this slice add SIMULATOR_SLICE_SIZE to encodeLength
            // if not, we need to trim the last match's matchLength and litLength
            if(index.encodeLength <= SIMULATOR_SLICE_SIZE) {
                // slice not full, concat lit to next seq
                concatLitLen += (SIMULATOR_SLICE_SIZE - index.encodeLength);
            } else {
                // NOTE HERE! slice overlapped with next slice, need trim;
                int overlapLen = index.encodeLength - SIMULATOR_SLICE_SIZE;
                while(overlapLen > 0) {
                    seqCount--;
                    if(outSeqs[seqCount].matchLength - 4 > overlapLen) {
                        // only need to trim the last match's matchLength
                        outSeqs[seqCount].matchLength -= overlapLen;
                        overlapLen = 0;
                        seqCount++;
                    } else if (outSeqs[seqCount].matchLength + outSeqs[seqCount].litLength > overlapLen) {
                        // also need to trim the last match's litLength
                        // remain litLength is concat to next slice's first seq
                        concatLitLen = outSeqs[seqCount].litLength - (overlapLen - outSeqs[seqCount].matchLength);
                        break;
                    } else {
                        // overlapped too much!!, drop the last seq
                        overlapLen -= outSeqs[seqCount].matchLength + outSeqs[seqCount].litLength;
                    }
                }
            }
        }
        index = nextIndex;
    }
    


    return seqCount;
}