silesia_file_name=(dickens mozilla mr nci ooffice reymont sao xml osdb samba webster x-ray)

for filename in ${silesia_file_name[@]}
do
  echo $filename
  ./externalSequenceProducer ~/hdd0/project/corpus/silesia/$filename ~/hdd0/project/corpus/silesia/$filename.seq_hlog13_wlog12_rSize4_rot8192
  ./externalSequenceProducer ~/hdd0/project/corpus/silesia/$filename ~/hdd0/project/corpus/silesia/$filename.seq_hlog15_wlog14_rSize4_rot8192
  ./externalSequenceProducer ~/hdd0/project/corpus/silesia/$filename ~/hdd0/project/corpus/silesia/$filename.seq_hlog17_wlog16_rSize4_rot8192
  ./externalSequenceProducer ~/hdd0/project/corpus/silesia/$filename ~/hdd0/project/corpus/silesia/$filename.seq_hlog19_wlog18_rSize4_rot8192
  ./externalSequenceProducer ~/hdd0/project/corpus/silesia/$filename ~/hdd0/project/corpus/silesia/$filename.seq_hlog21_wlog20_rSize4_rot8192
done
