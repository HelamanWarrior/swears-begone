#!/usr/bin/env bash
# Usage: ./mute_swears.sh subs.srt swears.txt input.mp4 output.mp4
# Automatically detects audio codec/bitrate/channels and preserves them.

set -e

# --- Initialize variables ---
SRT=""
INPUT=""
SWEARS=swears.txt
AUDIO_ONLY=false

# --- Parse arguments --- 
while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--transcript)
      SRT="$2"
      shift 2
      ;;
    -i|--input)
      INPUT="$2"
      shift 2
      ;;
    -s|--swears)
      SWEARS="$2"
      shift 2
      ;;
    -ao|--audio-only)
      AUDIO_ONLY=true 
      shift
      ;;
    -*)
      echo "Unknown option: $1"
      echo "Usage: $0 -t <subtitle> -i <video> [--process-audio]"
      exit 1
      ;;
    *)
      # (optional) handle positional args here
      shift
      ;;
    esac
done

# --- Video File Information ---
VIDEO_FILENAME="${INPUT%.*}"
EXTENSION="${INPUT##*.}"
OUTPUT="${VIDEO_FILENAME}[swears-cleaned].${EXTENSION}"

# Create lowercase, comma-separated list of swear words
SWEAR_LIST=$(grep -vi '^\s*$' "$SWEARS" | tr '[:upper:]' '[:lower:]' | tr '\n' ',' | sed 's/,$//')

TMP_SEGMENTS=$(mktemp)
TMP_MERGED=$(mktemp)
TMP_COUNT=$(mktemp)

# --- Extract swear segments from SRT ---
awk -v swearwords="$SWEAR_LIST" '
BEGIN {
  n = split(swearwords, sw, ",");
  for (i = 1; i <= n; i++) sw[i] = tolower(sw[i]);
  count = 0;
}
function in_swearlist(word) {
  lw = tolower(word);
  gsub(/[^a-z0-9'\''-]/, "", lw);
  for (i in sw) if (lw == sw[i]) return 1;
  return 0;
}
function to_seconds(t,    h,m,s,ms,parts,ss) {
  split(t, parts, ":");
  h = parts[1]; m = parts[2];
  split(parts[3], ss, ",");
  s = ss[1]; ms = ss[2];
  return h*3600 + m*60 + s + ms/1000;
}
/^[0-9]+$/ { next }
/-->/ {
  split($0, a, " ");
  start_s = to_seconds(a[1]);
  end_s   = to_seconds(a[3]);
  getline text;
  if (in_swearlist(text)) {
    printf "%.3f,%.3f\n", start_s, end_s;
    count++;
  }
}
END {
  print count > "/dev/stderr";  
}' "$SRT" 2> "$TMP_COUNT" | sort -n > "$TMP_SEGMENTS"

# --- Merge overlapping or adjacent ranges ---
awk -F, '
{
  if (NR == 1) {
    s = $1; e = $2;
  } else {
    if ($1 <= e + 0.15) {  # merge if overlap or within 150ms
      if ($2 > e) e = $2;
    } else {
      printf "%.3f,%.3f\n", s, e;
      s = $1; e = $2;
    }
  }
}
END {
  if (NR > 0) printf "%.3f,%.3f\n", s, e;
}' "$TMP_SEGMENTS" > "$TMP_MERGED"

SWEAR_COUNT=$(cat "$TMP_COUNT")
rm -f "$TMP_COUNT"

echo ""
echo "Detected $SWEAR_COUNT swear word(s) in subtitles."
echo ""

# --- Build ffmpeg filter string ---
FILTERS=""
while IFS=, read -r START END; do
  [ -z "$START" ] && continue
  [ -z "$FILTERS" ] || FILTERS+=","
  FILTERS+="volume=enable='between(t,$START,$END)':volume=0"
done < "$TMP_MERGED"

if [ -z "$FILTERS" ]; then
  echo "No swear words found. Copying input."
  cp "$INPUT" "$OUTPUT"
  rm -f "$TMP_SEGMENTS" "$TMP_MERGED"
  exit 0
fi

# --- Detect audio codec, bitrate, and channels ---
AUDIO_INFO=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,bit_rate,channels -of default=noprint_wrappers=1 "$INPUT")
AUDIO_CODEC=$(echo "$AUDIO_INFO" | grep codec_name | cut -d= -f2)
AUDIO_BITRATE=$(echo "$AUDIO_INFO" | grep bit_rate | cut -d= -f2)
AUDIO_CHANNELS=$(echo "$AUDIO_INFO" | grep channels | cut -d= -f2)

# Set fallback defaults if ffprobe didn’t return data
[ -z "$AUDIO_CODEC" ] && AUDIO_CODEC="aac"
[ -z "$AUDIO_BITRATE" ] && AUDIO_BITRATE="192000"
[ -z "$AUDIO_CHANNELS" ] && AUDIO_CHANNELS="2"

# Convert bitrate to ffmpeg-friendly format (e.g. 640000 -> 640k)
AUDIO_BITRATE_K=$((AUDIO_BITRATE / 1000))k

echo "Detected audio:"
echo "  Codec:    $AUDIO_CODEC"
echo "  Bitrate:  $AUDIO_BITRATE_K"
echo "  Channels: $AUDIO_CHANNELS"
echo ""

# --- Build ffmpeg command ---
CMD=""

if [[ "$AUDIO_ONLY" == false ]]; then
  # Create the final exported video with all the audio filters applied
  CMD="ffmpeg -hide_banner -v warning -stats -i \"$INPUT\" -af \"$FILTERS\" -c:v copy -c:a $AUDIO_CODEC -b:a $AUDIO_BITRATE_K -ac $AUDIO_CHANNELS \"$OUTPUT\" -y"

  # Create a file of the video filtering command (for archival)
  echo "$CMD" > "${INPUT%.*}[swears-cleaned].txt"
else
  # Generate an Audio file to be passed back into whisper
  CMD="ffmpeg -hide_banner -v warning -stats -i \"$INPUT\" -af \"$FILTERS\" -vn -ac 1 -y audio_processed.wav"
fi

echo "Generated ffmpeg command:"
echo "$CMD"

# Uncomment next line to execute automatically:
eval "$CMD"

rm -f "$TMP_SEGMENTS" "$TMP_MERGED"
