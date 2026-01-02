#!/bin/sh

thumb_dir="$HOME/.cache/thumbnails/cliphist"
screenshot_dir="$HOME/Pictures/Screenshots"
recording_dir="$HOME/Videos/Recordings"

mkdir -p "$thumb_dir"
mkdir -p "$screenshot_dir"
mkdir -p "$recording_dir"

screenshot_file="/tmp/screenshot.png"
recorder_pid_file="/tmp/wf-recorder.pid"

screen_thumb="$thumb_dir/screenshot_$(date +%Y-%m-%d_%H-%M-%S).png"
filepath="$screenshot_dir/screenshot_$(date +%Y-%m-%d_%H-%M-%S).png"

record_thumb="$thumb_dir/record_$(date +%Y-%m-%d_%H-%M-%S).mp4"
recpath="$recording_dir/record_$(date +%Y-%m-%d_%H-%M-%S).mp4"


ACTION="$1"

case "$ACTION" in
    "full")
        grim - | tee "$screenshot_file" | wl-copy -t image/png
        convert "$screenshot_file" -thumbnail 200 "$screen_thumb"
        notify-send "Screenshot" "Full screen copied to clipboard" -i "$screen_thumb"
        rm -f "$screenshot_file" "$screen_thumb"
        ;;
    "area")
        grim -g "$(slurp -b '00000075' -c '#b4befe' -d)" - | tee "$screenshot_file" | wl-copy -t image/png
        convert "$screenshot_file" -thumbnail 200 "$screen_thumb"
        notify-send "Screenshot" "Region copied to clipboard" -i "$screen_thumb"
        rm -f "$screenshot_file" "$screen_thumb"
        ;;
    "save-full")
        grim "$filepath"
        convert "$filepath" -thumbnail 200 "$screen_thumb"
        notify-send "Screenshot" "Full screen saved in \"Screenshots\" dir" -i "$screen_thumb"
        rm -f "$screen_thumb"
        ;;
    "save-area")
        grim -g "$(slurp -b '00000075' -c '#b4befe' -d)" "$filepath"
        convert "$filepath" -thumbnail 200 "$screen_thumb"
        notify-send "Screenshot" "Region saved in \"Screenshots\" dir" -i "$screen_thumb"
        rm -f "$screen_thumb"
        ;;
    "record-full-start")
        if [ -f "$recorder_pid_file" ]; then
            notify-send "Recording" "ERROR: Screen recorder already working" -i "$HOME/.icons/recording.png"
            exit 0
        fi
        wf-recorder -f "$recpath" &
        echo $! > "$recorder_pid_file"
        notify-send "Recording" "Screen recording started" -i "$HOME/.icons/recording.png"
        ;;
    "record-area-start")
        if [ -f "$recorder_pid_file" ]; then
            notify-send "Recording" "ERROR: Screen recorder already working" -i "$HOME/.icons/recording.png"
            exit 0
        fi

        area=$(slurp -b '00000075' -c '#b4befe' -d)
        scale=$(hyprctl monitors | grep scale | awk '{print $2}')
        read x y width height <<< $(echo "$area" | sed 's/[,x ]/ /g')

        Sx=$(printf "%.0f" "$(bc <<< "$x * $scale")")
        Sy=$(printf "%.0f" "$(bc <<< "$y * $scale")")
        Swidth=$(printf "%.0f" "$(bc <<< "$width * $scale")")
        Sheight=$(printf "%.0f" "$(bc <<< "$height * $scale")")

        scaled_area="$Sx,$Sy ${Swidth}x${Sheight}"

        wf-recorder -g "$scaled_area" -f "$recpath" &
        echo $! > "$recorder_pid_file"
        notify-send "Recording" "Area recording started" -i "$HOME/.icons/recording.png"
        ;;
    "record-stop")
        if [ ! -f "$recorder_pid_file" ]; then
            exit 0
        fi

        sleep 0.5
        kill -INT $(cat "$recorder_pid_file")
        rm "$recorder_pid_file"
        notify-send "Recording" "Recording stopped" -i "$HOME/.icons/recording.png"
        ;;
    "record-status")
        if [ ! -f "$recorder_pid_file" ]; then
            echo '{"text":"<span size=\"16000\" weight=\"bold\" color=\"#ff0000\">◉</span>", "tooltip":"Stopped"}'
            exit 0
        fi

        PID=$(cat "$recorder_pid_file")
        time=$(ps -p $(cat /tmp/wf-recorder.pid) -o etime= | awk '{print $1}')
        echo "{\"text\":\"<span size=\\\"12000\\\"><span weight=\\\"bold\\\" color=\\\"#ff0000\\\">◻</span> $time</span>\", \"tooltip\":\"Working\"}"
        ;;
    *)
        echo "ERROR: Unknown option"
        exit 1
        ;;
esac

