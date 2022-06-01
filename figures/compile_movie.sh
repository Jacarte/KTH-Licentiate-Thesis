#ffmpeg  -i out/img%03d.png -ss 5 -filter:v "scale=-1:2000" -loop_output 0 transit.gif
#ffmpeg -f image2 -framerate 24 -i out/img%03d.png -vf scale=2000x2000,transpose=1 out.gif

ffmpeg -i out/img%03d.png  -vf format=pal8 -pix_fmt rgb24 video.gif