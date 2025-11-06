#!/bin/bash

# AI Trade Explainer - Background Audio Generation Script
# Ta'limiy savdo tizimi uchun background audio yaratish

set -e  # Exit on any error

# Konfiguratsiya
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIO_DIR="$SCRIPT_DIR/audio"
TTS_SCRIPT="$SCRIPT_DIR/text_to_speech.py"
EDUCATIONAL_SCRIPT="$SCRIPT_DIR/educational_content.py"

# Papkalar yaratish
mkdir -p "$AUDIO_DIR"
mkdir -p "$AUDIO_DIR/backgrounds"
mkdir -p "$AUDIO_DIR/explanations"
mkdir -p "$AUDIO_DIR/educational"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Audio service check
check_audio_service() {
    if command -v ffmpeg &> /dev/null; then
        log "FFmpeg topildi"
        ffmpeg -version | head -1
    else
        log "XATOLIK: FFmpeg o'rnatilmagan"
        echo "O'rnatish uchun: sudo apt install ffmpeg"
        exit 1
    fi
}

# Test audio yaratish
create_test_audio() {
    log "Test audio yaratilmoqda..."
    
    # 10 soniyali sine wave test audio
    ffmpeg -f lavfi -i "sine=frequency=440:duration=10" \
           -ac 2 -ar 44100 \
           "$AUDIO_DIR/test_tone.wav" \
           -y 2>/dev/null
    
    log "Test audio yaratildi: $AUDIO_DIR/test_tone.wav"
}

# White noise background
create_white_noise() {
    local duration=${1:-300}  # Default 5 daqiqa
    local output_file="$AUDIO_DIR/backgrounds/white_noise.wav"
    
    log "White noise yaratilmoqda: ${duration} soniya"
    
    ffmpeg -f lavfi -i "anoisesrc=duration=$duration:color=white:seed=42" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Pink noise background
create_pink_noise() {
    local duration=${1:-300}
    local output_file="$AUDIO_DIR/backgrounds/pink_noise.wav"
    
    log "Pink noise yaratilmoqda: ${duration} soniya"
    
    ffmpeg -f lavfi -i "anoisesrc=duration=$duration:color=pink:seed=42" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Brown noise background
create_brown_noise() {
    local duration=${1:-300}
    local output_file="$AUDIO_DIR/backgrounds/brown_noise.wav"
    
    log "Brown noise yaratilmoqda: ${duration} soniya"
    
    ffmpeg -f lavfi -i "anoisesrc=duration=$duration:color=brown:seed=42" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Ambient soundscape
create_ambient_soundscape() {
    local duration=${1:-300}
    local output_file="$AUDIO_DIR/backgrounds/ambient.wav"
    
    log "Ambient soundscape yaratilmoqda: ${duration} soniya"
    
    # Multiple layers of ambient sound
    ffmpeg -f lavfi -i "anoisesrc=duration=$duration:color=pink:seed=1" \
           -f lavfi -i "anoisesrc=duration=$duration:color=brown:seed=2" \
           -f lavfi -i "anoisesrc=duration=$duration:color=white:seed=3" \
           -filter_complex "
           [0]volume=0.3,lowpass=f=2000[pink_layer];
           [1]volume=0.2,highpass=f=100[brown_layer];
           [2]volume=0.1,bandpass=f=1000:width_type=h:w=500[white_layer];
           [pink_layer][brown_layer][white_layer]amix=inputs=3:duration=longest
           " \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Binaural beats yaratish
create_binaural_beats() {
    local base_freq=${1:-200}  # Hz
    local beat_freq=${2:-8}    # Hz (Alpha waves uchun)
    local duration=${3:-600}   # 10 daqiqa
    local output_file="$AUDIO_DIR/backgrounds/binaural_${base_freq}_${beat_freq}.wav"
    
    log "Binaural beats yaratilmoqda: ${base_freq}Hz, ${beat_freq}Hz beat"
    
    # Left channel: base frequency
    # Right channel: base + beat frequency
    ffmpeg -f lavfi -i "sine=frequency=$base_freq:duration=$duration" \
           -f lavfi -i "sine=frequency=$((base_freq + beat_freq)):duration=$duration" \
           -filter_complex "[0]volume=0.5[left];[1]volume=0.5[right];[left][right]amix=inputs=2:duration=longest" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Voice overlay qo'shish
add_voice_overlay() {
    local audio_file="$1"
    local voice_file="$2"
    local output_file="$3"
    local voice_volume=${4:-0.7}
    local background_volume=${5:-0.3}
    
    log "Voice overlay qo'shilmoqda..."
    
    ffmpeg -i "$audio_file" \
           -i "$voice_file" \
           -filter_complex "
           [0]volume=$background_volume[bg];
           [1]volume=$voice_volume[voice];
           [bg][voice]amix=inputs=2:duration=longest
           " \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Audio fade in/out
add_fade_effect() {
    local input_file="$1"
    local output_file="$2"
    local fade_in=${3:-5}     # seconds
    local fade_out=${4:-5}    # seconds
    
    log "Fade effect qo'shilmoqda..."
    
    ffmpeg -i "$input_file" \
           -af "afade=t=in:ss=0:d=$fade_in,afade=t=out:st=$(($(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$input_file") - fade_out)):d=$fade_out" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Educational voice generation (placeholder)
generate_educational_voice() {
    local text="$1"
    local output_file="$2"
    
    log "Ta'limiy voice yaratilmoqda: '$text'"
    
    # Placeholder - bu yerda TTS engine ulanadi
    # Hozircha silence yaratamiz
    ffmpeg -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=44100" \
           -t 10 \
           -c:a pcm_s16le \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Trade explanation audio yaratish
create_trade_explanation_audio() {
    local signal_type="$1"
    local explanation_text="$2"
    local output_file="$AUDIO_DIR/explanations/${signal_type}_explanation.wav"
    
    log "Trade explanation audio yaratilmoqda..."
    
    # Explanation text dan audio yaratish
    if [[ -f "$TTS_SCRIPT" ]]; then
        python3 "$TTS_SCRIPT" --text "$explanation_text" --output "$output_file" --voice "explanation_voice"
    else
        log "TTS skript topilmadi, placeholder audio yaratilmoqda"
        ffmpeg -f lavfi -i "anullsrc=channel_layout=stereo:sample_rate=44100" \
               -t 30 \
               -c:a pcm_s16le \
               "$output_file" \
               -y 2>/dev/null
    fi
    
    echo "$output_file"
}

# Progress beep sounds
create_progress_beeps() {
    local output_dir="$AUDIO_DIR/beeps"
    mkdir -p "$output_dir"
    
    log "Progress beep sounds yaratilmoqda..."
    
    # Success beep
    ffmpeg -f lavfi -i "sine=frequency=800:duration=0.2" \
           -af "afade=t=in:ss=0:d=0.05,afade=t=out:st=0.15:d=0.05" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_dir/success.wav" \
           -y 2>/dev/null
    
    # Warning beep  
    ffmpeg -f lavfi -i "sine=frequency=400:duration=0.3" \
           -af "afade=t=in:ss=0:d=0.1,afade=t=out:st=0.2:d=0.1" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_dir/warning.wav" \
           -y 2>/dev/null
    
    # Error beep
    ffmpeg -f lavfi -i "sine=frequency=200:duration=0.5" \
           -af "afade=t=in:ss=0:d=0.1,afade=t=out:st=0.4:d=0.1" \
           -ac 2 -ar 44100 -c:a pcm_s16le \
           "$output_dir/error.wav" \
           -y 2>/dev/null
    
    echo "Progress beeps created in $output_dir"
}

# Interactive audio feedback
create_interactive_feedback() {
    local action="$1"  # click, hover, complete, etc.
    local output_file="$AUDIO_DIR/interactive/${action}_sound.wav"
    
    mkdir -p "$AUDIO_DIR/interactive"
    
    case "$action" in
        "click")
            ffmpeg -f lavfi -i "sine=frequency=1000:duration=0.1" \
                   -af "afade=t=in:ss=0:d=0.02,afade=t=out:st=0.08:d=0.02" \
                   -ac 2 -ar 44100 -c:a pcm_s16le \
                   "$output_file" -y 2>/dev/null
            ;;
        "hover")
            ffmpeg -f lavfi -i "sine=frequency=600:duration=0.05" \
                   -af "afade=t=in:ss=0:d=0.01,afade=t=out:st=0.04:d=0.01" \
                   -ac 2 -ar 44100 -c:a pcm_s16le \
                   "$output_file" -y 2>/dev/null
            ;;
        "complete")
            ffmpeg -f lavfi -i "sine=frequency=523:duration=0.2" \
                   -f lavfi -i "sine=frequency=659:duration=0.2" \
                   -f lavfi -i "sine=frequency=784:duration=0.2" \
                   -filter_complex "[0][1][2]concat=n=3:v=0:a=1[out]" \
                   -map "[out]" \
                   -ac 2 -ar 44100 -c:a pcm_s16le \
                   "$output_file" -y 2>/dev/null
            ;;
        *)
            log "Noma'lum action: $action"
            return 1
            ;;
    esac
    
    echo "$output_file"
}

# Loop audio file
create_looping_audio() {
    local input_file="$1"
    local output_file="$2"
    local loop_count=${3:-10}  # 10 marta takrorlash
    
    log "Audio fayl loop yaratilmoqda..."
    
    # Input faylni loop qilish
    ffmpeg -stream_loop $((loop_count - 1)) -i "$input_file" \
           -c copy \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Audio compression
compress_audio() {
    local input_file="$1"
    local output_file="$2"
    local bitrate=${3:-128k}
    
    log "Audio fayl siqilmoqda: $bitrate"
    
    ffmpeg -i "$input_file" \
           -c:a libmp3lame -b:a "$bitrate" \
           "$output_file" \
           -y 2>/dev/null
    
    echo "$output_file"
}

# Batch processing
batch_process_backgrounds() {
    log "Batch background audio yaratish boshlandi..."
    
    # Turli xil duration'lar
    for duration in 300 600 900; do  # 5, 10, 15 daqiqa
        create_white_noise $duration
        create_pink_noise $duration
        create_brown_noise $duration
        create_ambient_soundscape $duration
    done
    
    # Binaural beats variants
    for base_freq in 100 200 300; do
        for beat_freq in 8 10 12; do  # Alpha, Beta, Gamma waves
            create_binaural_beats $base_freq $beat_freq 600
        done
    done
    
    log "Batch processing tugallandi"
}

# Audio info olish
get_audio_info() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "Fayl topilmadi: $file"
        return 1
    fi
    
    log "Audio fayl ma'lumotlari:"
    
    # Duration
    duration=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$file")
    echo "Duration: ${duration} soniya"
    
    # Sample rate
    sample_rate=$(ffprobe -v quiet -show_entries stream=sample_rate -of csv=p=0 "$file" | head -1)
    echo "Sample Rate: ${sample_rate} Hz"
    
    # Channels
    channels=$(ffprobe -v quiet -show_entries stream=channels -of csv=p=0 "$file" | head -1)
    echo "Channels: $channels"
    
    # Bit depth
    bit_depth=$(ffprobe -v quiet -show_entries stream=bits_per_sample -of csv=p=0 "$file" | head -1)
    echo "Bit Depth: $bit_depth bits"
}

# Main menu
show_menu() {
    echo ""
    echo "=== AI Trade Explainer Audio Generator ==="
    echo ""
    echo "1. Check audio service"
    echo "2. Create test audio"
    echo "3. Create white noise (5 min)"
    echo "4. Create pink noise (5 min)"
    echo "5. Create brown noise (5 min)"
    echo "6. Create ambient soundscape (5 min)"
    echo "7. Create binaural beats"
    echo "8. Create progress beeps"
    echo "9. Batch process backgrounds"
    echo "10. Get audio info"
    echo "0. Exit"
    echo ""
    echo -n "Tanlang: "
}

# Main script
main() {
    log "AI Trade Explainer Audio Generator boshlandi"
    
    # Create all initial audio files
    create_test_audio
    create_progress_beeps
    
    # Interactive menu
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                check_audio_service
                ;;
            2)
                create_test_audio
                ;;
            3)
                create_white_noise 300
                ;;
            4)
                create_pink_noise 300
                ;;
            5)
                create_brown_noise 300
                ;;
            6)
                create_ambient_soundscape 300
                ;;
            7)
                echo -n "Base frequency (Hz): "
                read -r base_freq
                echo -n "Beat frequency (Hz): "
                read -r beat_freq
                create_binaural_beats $base_freq $beat_freq 600
                ;;
            8)
                create_progress_beeps
                ;;
            9)
                batch_process_backgrounds
                ;;
            10)
                echo -n "Audio fayl yo'li: "
                read -r audio_file
                get_audio_info "$audio_file"
                ;;
            0)
                log "Dastur tugallandi"
                exit 0
                ;;
            *)
                echo "Noto'g'ri tanlov"
                ;;
        esac
        
        echo -n "Davom etish uchun Enter bosing..."
        read -r
    done
}

# Script arguments
if [[ $# -gt 0 ]]; then
    case $1 in
        "check")
            check_audio_service
            ;;
        "test")
            create_test_audio
            ;;
        "white-noise")
            create_white_noise ${2:-300}
            ;;
        "pink-noise")
            create_pink_noise ${2:-300}
            ;;
        "brown-noise")
            create_brown_noise ${2:-300}
            ;;
        "ambient")
            create_ambient_soundscape ${2:-300}
            ;;
        "binaural")
            create_binaural_beats ${2:-200} ${3:-8} ${4:-600}
            ;;
        "beeps")
            create_progress_beeps
            ;;
        "batch")
            batch_process_backgrounds
            ;;
        *)
            echo "Foydalanish: $0 [check|test|white-noise|pink-noise|brown-noise|ambient|binaural|batch]"
            echo "Binaural misol: $0 binaural 200 8 600"
            ;;
    esac
else
    # Interactive mode
    main
fi