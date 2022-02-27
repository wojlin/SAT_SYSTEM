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
echo -e "\e[96m@@@@@@@@                 APT CLI CONVERTER                 @@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e ""

echo -e "\e[96mfrequency:\033[0m ${freq}MHz\033[0m"
echo -e "\e[96mtime:\033[0m ${timer}s\033[0m"
echo -e "\e[96mname:\033[0m ${name}\033[0m"

mkdir "${process}/${name}"


echo ""
echo -e "\e[96mstep 1: recording samples... (this will take 10 minutes)\033[0m"

echo -e "\033[90m"
timeout "${timer}"s rtl_fm -M fm -g 70 -d 0 -s 48000 -f "${freq}M" > "${process}/${name}/raw.raw"
echo -e "\033[0m"

echo -e "\e[96mstep 2: converting raw file to wav...\033[0m"

echo -e "\033[90m"
sox -t raw -e signed-integer -b 16 -r 48000 -c 1 "${process}/${name}/raw.raw" -t wav -r 48000 "${process}/${name}/wav.wav" -V3
echo -e "\033[0m"


echo -e "\e[96mstep 3: converting wav file to image...\033[0m"
echo ""

noaa-apt --output "${process}/${name}/output.png" --contrast "histogram" "${process}/${name}/wav.wav"
cp "${process}/${name}/output.png" "${output}/${name}.png"

echo -e "\033[0m"

echo -e "\e[96mimage received!\033[0m"
echo ""

tiv "${process}/${name}/output.png" -w 70

echo ""
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@                        END                        @@@@@@@@@@@\033[0m"
echo -e "\e[96m@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\033[0m"

sleep 60
