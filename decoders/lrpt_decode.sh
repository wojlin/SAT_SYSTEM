#! /usr/bin/bash


if [ $# -ne 14 ]
  then
    echo -e "\e[31mERROR: script need 7 arguments: -n <name> -f <freq> -t <time to listen> -p <process path> -o <output path> -m <metadata> -d <delete temp>\033[0m"
fi


while getopts ":n:f:t:p:o:m:d:" opt; do
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
    m) metadata="$OPTARG"
    ;;
    d) delete="$OPTARG"
    ;;
    \?) echo -e "\e[31mERROR:Invalid option -$OPTARG\033[0m" >&2
    ;;
  esac

  case $OPTARG in
    -*) echo -e "\e[31mERROR:Option $opt needs a valid argument\033[0m"
    ;;
  esac
done

lower_delete=${delete,,}

echo -e "\e[96mdecoder     : \033[0m LRPT \033[0m"
echo -e "\e[96mfrequency   : \033[0m ${freq}MHz\033[0m"
echo -e "\e[96mtime        : \033[0m ${timer}s\033[0m"
echo -e "\e[96mname        : \033[0m ${name}\033[0m"
echo -e "\e[96mdelete temp : \033[0m ${lower_delete}\033[0m"

if [ -d "${process}/${name}" ]; then
  echo ""
  echo -e "\u001b[38;5;196mcannot create dir: '${process}/${name}' already exist! aborting... \033[0m"
  sleep 10
  exit
else
  mkdir "${process}/${name}"
fi


echo ""
echo -e "\e[96mstep 1: recording samples... (this will take ${timer} seconds)\033[0m"
echo ""

timeout ${timer}s rtl_fm -M raw -s 280000 -f "${freq}"M -E dc -g 70 -p 1 > "${process}/${name}/meteor.raw"

echo ""
echo -e "\e[96mstep 2: converting raw file to wav...\033[0m"
echo ""

sox -t raw -esigned-integer -b16 -r 280000 -c 2 "${process}/${name}/meteor.raw" -t wav "${process}/${name}/meteor.wav"

echo ""
echo -e "\e[96mstep 3: demodulating wav file to s file...\033[0m"
echo ""

meteor_demod -O 8 -f 128 -m qpsk "${process}/${name}/meteor.wav" -o "${process}/${name}/meteor.s" -B

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


echo ""
echo -e "\e[96mstep 6: writing metadata to output file...\033[0m"
echo ""

python3 decoders/metadata.py "${output}"/"${name}".png "${metadata}"

if [ "$lower_delete" == "true" ]; then
    echo ""
    echo -e "\e[96mstep 7: deleting temp files directory...\033[0m"
    echo ""
    dir="${process}/${name}"
    if [ "$dir" == "/" ]; then
      echo -e "\u001b[38;5;196mtrying to delete root dir!!! aborting... \033[0m"
      sleep 10
      exit
    else
      rm -rf "${dir:?}/"
    fi
fi

tiv "${output}"/"${name}".png -w 70

echo ""
echo -e "\e[96mdecoding done!\033[0m"
sleep 60
exit