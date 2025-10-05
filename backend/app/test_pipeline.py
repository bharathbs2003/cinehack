"""
Test script for the dubbing pipeline.
Use this to test the pipeline with a sample video.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipeline import DubbingPipeline
from app.validation import DubbingValidator
import json


def progress_callback(stage: str, progress: int, message: str = ""):
    """Print progress updates."""
    print(f"[{progress:3d}%] {stage:20s} | {message}")


def test_pipeline(video_path: str, target_lang: str = "hi"):
    """
    Test the complete dubbing pipeline.
    
    Args:
        video_path: Path to test video
        target_lang: Target language code
    """
    print("=" * 70)
    print("EduDub AI - Pipeline Test")
    print("=" * 70)
    print(f"Video: {video_path}")
    print(f"Target Language: {target_lang}")
    print("=" * 70)
    print()
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        return False
        
    # Initialize pipeline
    print("🔧 Initializing pipeline...")
    pipeline = DubbingPipeline(
        use_whisperx=True,
        use_diarization=True,
        use_emotion=True,
        use_elevenlabs=False,  # Set to True if you have API key
        use_wav2lip=False  # Set to True if Wav2Lip is set up
    )
    
    try:
        # Run pipeline
        print("🚀 Starting dubbing process...\n")
        result = pipeline.process(
            video_path=video_path,
            target_language=target_lang,
            source_language="en",
            output_dir="test_output",
            progress_callback=progress_callback
        )
        
        print("\n" + "=" * 70)
        print("✅ Pipeline completed successfully!")
        print("=" * 70)
        
        # Print results
        print("\n📊 Results:")
        print(f"  Job ID:        {result['job_id']}")
        print(f"  Final Video:   {result['final_video_path']}")
        print(f"  Dubbed Audio:  {result['dubbed_audio_path']}")
        
        metadata = result.get('metadata', {})
        print(f"\n📈 Statistics:")
        print(f"  Segments:      {metadata.get('num_segments', 0)}")
        print(f"  Speakers:      {metadata.get('num_speakers', 0)}")
        print(f"  Duration:      {metadata.get('duration_seconds', 0):.2f}s")
        
        # Save transcript
        transcript_path = os.path.join("test_output", "test_transcript.json")
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(result['transcript'], f, ensure_ascii=False, indent=2)
        print(f"  Transcript:    {transcript_path}")
        
        # Validate output
        print("\n🔍 Validating output...")
        validator = DubbingValidator()
        validation_results = validator.validate_output(
            original_video_path=video_path,
            dubbed_video_path=result['final_video_path'],
            transcript_path=transcript_path
        )
        
        print(f"  Overall Status: {validation_results['overall_status'].upper()}")
        
        for check_name, check_result in validation_results['checks'].items():
            status = "✅" if check_result.get('passed', False) else "❌"
            print(f"  {status} {check_name}: {check_result.get('message', 'N/A')}")
            
        print("\n" + "=" * 70)
        
        return validation_results['overall_status'] == 'pass'
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test with command line arguments or default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        target_lang = sys.argv[2] if len(sys.argv) > 2 else "hi"
    else:
        print("Usage: python test_pipeline.py <video_path> [target_lang]")
        print("\nExample: python test_pipeline.py sample.mp4 hi")
        print("\nYou can also edit this file to set a default test video.")
        sys.exit(1)
        
    # Run test
    success = test_pipeline(video_path, target_lang)
    
    sys.exit(0 if success else 1)

