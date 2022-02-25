#! /usr/bin/bash


if [ $# -ne 8 ]
  then
    echo -e "\e[31mERROR: script need 4 arguments: -s <satellite name> -f <frequency in MHz> -n <name> -t <time to listen>\033[0m"
    exit
fi


while getopts ":f:n:t:s:" opt; do
  case $opt in
    f) freq="$OPTARG"
    ;;
    n) name="$OPTARG"
    ;;
    t) timer="$OPTARG"
    ;;
    s) sat="$OPTARG"
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
echo -e "\e[96msatellite:\033[0m ${sat}\033[0m"
echo -e "\e[96mfrequency:\033[0m ${freq}MHz\033[0m"
echo -e "\e[96mtime:\033[0m ${timer}s\033[0m"
echo -e "\e[96mname:\033[0m ${name}\033[0m"


mkdir temp/${name}


#timeout ${timer}s rtl_fm -M fm -g 50 -d 0 -s 48000 -f "${freq}M" > "temp/${name}/raw.raw"

#: '
###### no GUI ######
echo ""
echo -e "\e[96mstep 1: recording samples... (this will take 10 minutes)\033[0m"

echo -e "\033[90m"
timeout ${timer}s rtl_fm -M fm -g 70 -d 0 -s 48000 -f "${freq}M" > "temp/${name}/raw.raw"
echo -e "\033[0m"

echo -e "\e[96mstep 2: converting raw file to wav...\033[0m"

echo -e "\033[90m"
sox -t raw -e signed-integer -b 16 -r 48000 -c 1 "temp/${name}/raw.raw" -t wav -r 48000 "temp/${name}/wav.wav" -V3
echo -e "\033[0m"
#####################
#'

echo -e "\e[96mstep 3: cvonverting wav file to image...\033[0m"
echo ""

noaa-apt --output "temp/${name}/output.png" --sat ${sat} --contrast "histogram" "temp/${name}/wav.wav"
echo -e "\033[0m"

echo -e "\e[96mimage received!\033[0m"
echo ""

tiv "temp/${name}/output.png" -w 70

echo ""
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@                        END                        @@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"


