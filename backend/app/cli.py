"""
Command-line interface for video dubbing.
Allows running dubbing without the web server.
"""
import argparse
import sys
import os
from pathlib import Path
from .pipeline import DubbingPipeline
from .config import settings
import json


def progress_callback(stage: str, progress: int, message: str = ""):
    """Print progress updates."""
    print(f"[{progress}%] {stage}: {message}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="EduDub AI - Video Dubbing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m app.cli --input video.mp4 --lang hi --output output/

  # With all features
  python -m app.cli --input video.mp4 --lang es --output output/ \\
    --whisperx --diarization --emotion --elevenlabs --wav2lip

  # Specify speaker count
  python -m app.cli --input video.mp4 --lang fr --min-speakers 2 --max-speakers 4

Supported languages:
  en (English), hi (Hindi), es (Spanish), fr (French), de (German),
  zh (Chinese), ja (Japanese), ko (Korean), ar (Arabic), pt (Portuguese),
  ru (Russian), it (Italian), mr (Marathi), bn (Bengali), ta (Tamil), te (Telugu)
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input video file"
    )
    
    parser.add_argument(
        "--lang", "-l",
        required=True,
        help="Target language code (e.g., hi, es, fr)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output/)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--source-lang",
        default="en",
        help="Source language code (default: en)"
    )
    
    # Feature flags
    parser.add_argument(
        "--whisperx",
        action="store_true",
        help="Use WhisperX for transcription"
    )
    
    parser.add_argument(
        "--diarization",
        action="store_true",
        help="Enable speaker diarization"
    )
    
    parser.add_argument(
        "--emotion",
        action="store_true",
        help="Enable emotion detection"
    )
    
    parser.add_argument(
        "--elevenlabs",
        action="store_true",
        help="Use ElevenLabs TTS (requires API key)"
    )
    
    parser.add_argument(
        "--wav2lip",
        action="store_true",
        help="Enable Wav2Lip lip-sync"
    )
    
    # Speaker configuration
    parser.add_argument(
        "--min-speakers",
        type=int,
        help="Minimum number of speakers for diarization"
    )
    
    parser.add_argument(
        "--max-speakers",
        type=int,
        help="Maximum number of speakers for diarization"
    )
    
    # Output options
    parser.add_argument(
        "--save-transcript",
        action="store_true",
        default=True,
        help="Save transcript JSON (default: True)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)
        
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Print configuration
    print("="*60)
    print("EduDub AI - Video Dubbing CLI")
    print("="*60)
    print(f"Input:           {args.input}")
    print(f"Target Language: {args.lang}")
    print(f"Source Language: {args.source_lang}")
    print(f"Output:          {args.output}")
    print(f"WhisperX:        {args.whisperx}")
    print(f"Diarization:     {args.diarization}")
    print(f"Emotion:         {args.emotion}")
    print(f"ElevenLabs:      {args.elevenlabs}")
    print(f"Wav2Lip:         {args.wav2lip}")
    print("="*60)
    
    # Initialize pipeline
    pipeline = DubbingPipeline(
        use_whisperx=args.whisperx,
        use_diarization=args.diarization,
        use_emotion=args.emotion,
        use_elevenlabs=args.elevenlabs,
        use_wav2lip=args.wav2lip
    )
    
    # Process video
    try:
        result = pipeline.process(
            video_path=args.input,
            target_language=args.lang,
            source_language=args.source_lang,
            output_dir=args.output,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers,
            progress_callback=progress_callback if args.verbose else None
        )
        
        # Print results
        print("\n" + "="*60)
        print("✅ Dubbing Complete!")
        print("="*60)
        print(f"Final Video:     {result['final_video_path']}")
        print(f"Dubbed Audio:    {result['dubbed_audio_path']}")
        print(f"Job ID:          {result['job_id']}")
        
        metadata = result.get('metadata', {})
        print(f"\nMetadata:")
        print(f"  Segments:      {metadata.get('num_segments', 0)}")
        print(f"  Speakers:      {metadata.get('num_speakers', 0)}")
        print(f"  Duration:      {metadata.get('duration_seconds', 0):.2f}s")
        
        # Save transcript
        if args.save_transcript:
            transcript_path = os.path.join(args.output, "transcript.json")
            with open(transcript_path, "w", encoding="utf-8") as f:
                json.dump(result['transcript'], f, ensure_ascii=False, indent=2)
            print(f"  Transcript:    {transcript_path}")
        
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

