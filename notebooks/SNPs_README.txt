Column headings:
1) Chr
2) Position (hg38)
3) SNP ID
4) Reference allele
5) Alternate allele

File descriptions:
SNPs_random.txt (n=10000): set of random noncoding SNPs
SNPs_allRetina.txt (n=7034): all retinal disease SNPs
SNPs_overlapPeaksRetina.txt (n=1152): retinal disease SNPs overlapping scATAC peaks
SNPs_Tier3Retina.txt (n=413): prioritized list of retinal disease SNPs
SNPs_Tier2Retina.txt (n=205): further prioritized list of retinal disease SNPs

Figure ideas:
- schematic of BPNet
- bar graph of "scores" - can compare different SNP categories (would definitely include random, all retina, and SNPs overlapping peaks)
- 1-2 examples of prioritized/high "score" SNPs

`bedtools intersect -a <(cat SNPs/SNPs_random.txt  | awk -v OFS='\t' '{print $1,$2,$2+1,$3,$4,$5}') -b <(cat peaks/orig_calls/*) -wa -u | cut -f1,2,4- > SNPs/SNPs_randomInPeaks.txt`
