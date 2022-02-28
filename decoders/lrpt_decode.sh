#! /usr/bin/bash

if [ $# -ne 10 ]
  then
    echo -e "\e[31mERROR: script need 5 arguments: -n <name> -f <freq> -t <time to listen> -p <process path> -o <output path>\033[0m"
fi


while getopts ":n:f:t:p:o:" opt; do
  case $opt in
    n) name="$OPTARG"
    ;;
    f) freq="$OPTARG"
    ;;
    t) timer="$OPTARG"
    ;;
    p) process="$OPTARG"
    ;;
    o) output="$OPTARG"
    ;;
    \?) echo -e "\e[31mERROR:Invalid option -$OPTARG\033[0m" >&2
    ;;
  esac

  case $OPTARG in
    -*) echo -e "\e[31mERROR:Option $opt needs a valid argument\033[0m"
    ;;
  esac
done

echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@                LRPT CLI CONVERTER                 @@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e ""
echo -e "\e[96mfrequency:\033[0m ${freq}MHz\033[0m"
echo -e "\e[96mtime:\033[0m ${timer}s\033[0m"
echo -e "\e[96mname:\033[0m ${name}\033[0m"

mkdir "${process}/${name}"

echo ""
echo -e "\e[96mstep 1: recording samples... (this will take 10 minutes)\033[0m"
echo ""

timeout ${timer}s rtl_fm -M raw -s 280000 -f "${freq}"M -E dc -g 70 -p 1 > "${process}/${name}/meteor.raw"

echo ""
echo -e "\e[96mstep 2: converting raw file to wav...\033[0m"
echo ""

sox -t raw -esigned-integer -b16 -r 280000 -c 2 "${process}/${name}/meteor.raw" -t wav "${process}/${name}/meteor.wav"

echo ""
echo -e "\e[96mstep 3: demodulating wav file to s file...\033[0m"
echo ""

meteor_demod -O 8 -f 128 -m qpsk "${process}/${name}/meteor.wav" -o "${process}/${name}/meteor.s"

echo ""
echo -e "\e[96mstep 4: decoding s file...\033[0m"
echo ""

meteor_decode -o "${process}/${name}/meteor.png" --apid 65,65,64 -B "${process}/${name}/meteor.s"

echo ""
echo -e "\e[96mstep 5: rectifing output image...\033[0m"
echo ""

python3 decoders/rectify.py "${process}/${name}/meteor.png"

echo ""
echo -e "\e[96mimage received!\033[0m"
echo ""

cp "${process}/${name}"/meteor-rectified.png "${output}"/"${name}".png

echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@                   END                   @@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"

sleep 60

