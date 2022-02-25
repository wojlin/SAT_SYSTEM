#! /usr/bin/bash


if [ $# -ne 4 ]
  then
    echo -e "\e[31mERROR: script need 2 arguments: -n <name> -t <time to listen>\033[0m"
    exit
fi


while getopts ":n:t:" opt; do
  case $opt in
    n) name="$OPTARG"
    ;;
    t) timer="$OPTARG"
    ;;
    \?) echo -e "\e[31mERROR:Invalid option -$OPTARG\033[0m" >&2
    exit 1
    ;;
  esac

  case $OPTARG in
    -*) echo -e "\e[31mERROR:Option $opt needs a valid argument\033[0m"
    exit 1
    ;;
  esac
done

echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@                 APT CLI CONVERTER                 @@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e ""
echo -e "\e[96mtime:\033[0m ${timer}s\033[0m"
echo -e "\e[96mname:\033[0m ${name}\033[0m"

mkdir temp/${name}

echo ""
echo -e "\e[96mstep 1: recording samples... (this will take 10 minutes)\033[0m"
echo ""

timeout ${timer}s rtl_fm -M raw -s 280000 -f 137.1M -E dc -g 70 -p 1 > temp/${name}/meteor.raw

echo ""
echo -e "\e[96mstep 2: converting raw file to wav...\033[0m"
echo ""

sox -t raw -esigned-integer -b16 -r 280000 -c 2 "temp/${name}/meteor.raw" -t wav "temp/${name}/meteor.wav"

echo ""
echo -e "\e[96mstep 3: demodulating wav file to s file...\033[0m"
echo ""

meteor_demod -O 8 -f 128 -m qpsk temp/${name}/meteor.wav -o temp/${name}/meteor.s

echo ""
echo -e "\e[96mstep 4: decoding s file...\033[0m"
echo ""

meteor_decode -o temp/${name}/meteor.png  --apid 65,65,64 -B temp/${name}/meteor.s

echo ""
echo -e "\e[96mstep 5: rectifing output image...\033[0m"
echo ""

python3 rectify.py temp/${name}/meteor.png

echo ""
echo -e "\e[96mimage received!\033[0m"
echo ""

echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@                   END                   @@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"


