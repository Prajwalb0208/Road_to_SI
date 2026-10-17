#!/usr/bin/env bash
# Screen recorder for tutorial footage (whole desktop, 30 fps, NVENC, MKV so a hard stop is safe).
#   rec.sh start <out.mkv> [maxSeconds]   -> records in background, pid in $TMPDIR/rec.pid
#   rec.sh stop                            -> stops it (sends q, falls back to kill)
set -u
PIDF="${TMP:-/tmp}/rec.pid"
case "$1" in
  start)
    out="$2"; max="${3:-600}"
    mkdir -p "$(dirname "$out")"
    # stdin from a fifo-like file so we can send 'q'
    CTL="${TMP:-/tmp}/rec.ctl"; : > "$CTL"
    (tail -f "$CTL" | ffmpeg -hide_banner -loglevel error -y -f gdigrab -framerate 30 -draw_mouse 1 -t "$max" -i desktop \
      -c:v h264_nvenc -preset p5 -rc vbr -cq 19 -pix_fmt yuv420p -f matroska "$out") &
    echo $! > "$PIDF"; sleep 1; echo "rec start $out" ;;
  stop)
    CTL="${TMP:-/tmp}/rec.ctl"; echo q >> "$CTL"; sleep 3
    pkill -f "tail -f $CTL" 2>/dev/null
    if tasklist | grep -qi ffmpeg; then sleep 3; fi
    echo "rec stop" ;;
esac
