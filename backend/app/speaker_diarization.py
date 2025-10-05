"""
Speaker diarization for identifying and tracking different speakers in audio.
Uses transcript segments and simple heuristics to identify speaker changes.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional


def detect_speaker_changes(segments: List[Dict], silence_threshold: float = 0.5) -> List[Dict]:
    """
    Detect speaker changes based on pauses and segment patterns.
    
    Args:
        segments: List of transcript segments with start/end times
        silence_threshold: Minimum silence duration to consider speaker change (seconds)
    
    Returns:
        List of segments with speaker IDs assigned
    """
    if not segments:
        return []
    
    # Assign speaker IDs based on pauses
    speaker_id = 0
    speaker_segments = []
    
    for i, segment in enumerate(segments):
        # Check pause before this segment
        if i > 0:
            prev_segment = segments[i - 1]
            pause_duration = segment['start'] - prev_segment['end']
            
            # If significant pause, assume speaker change
            if pause_duration > silence_threshold:
                speaker_id += 1
        
        segment_with_speaker = segment.copy()
        segment_with_speaker['speaker'] = f"SPEAKER_{speaker_id:02d}"
        speaker_segments.append(segment_with_speaker)
    
    print(f"Detected {speaker_id + 1} speakers based on pauses")
    return speaker_segments


def merge_consecutive_speaker_segments(segments: List[Dict]) -> List[Dict]:
    """
    Merge consecutive segments from the same speaker.
    """
    if not segments:
        return []
    
    merged = []
    current_segment = segments[0].copy()
    
    for i in range(1, len(segments)):
        segment = segments[i]
        
        # If same speaker and close in time, merge
        if (segment['speaker'] == current_segment['speaker'] and 
            segment['start'] - current_segment['end'] < 1.0):
            
            # Merge text
            current_segment['text'] += " " + segment['text']
            current_segment['end'] = segment['end']
            
            # Merge words if available
            if 'words' in current_segment and 'words' in segment:
                current_segment['words'].extend(segment['words'])
        else:
            # Different speaker or large gap
            merged.append(current_segment)
            current_segment = segment.copy()
    
    # Add last segment
    merged.append(current_segment)
    
    print(f"Merged {len(segments)} segments into {len(merged)} speaker turns")
    return merged


def analyze_speaker_patterns(segments: List[Dict]) -> Dict[str, Dict]:
    """
    Analyze patterns for each speaker (duration, word count, etc.)
    """
    speaker_stats = {}
    
    for segment in segments:
        speaker = segment['speaker']
        
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                'total_duration': 0.0,
                'total_words': 0,
                'segment_count': 0,
                'texts': []
            }
        
        duration = segment['end'] - segment['start']
        word_count = len(segment['text'].split())
        
        speaker_stats[speaker]['total_duration'] += duration
        speaker_stats[speaker]['total_words'] += word_count
        speaker_stats[speaker]['segment_count'] += 1
        speaker_stats[speaker]['texts'].append(segment['text'])
    
    return speaker_stats


def detect_speaker_genders(speaker_stats: Dict[str, Dict]) -> Dict[str, str]:
    """
    Detect gender of each speaker using simple heuristics.
    
    In production, this should use:
    - Audio analysis (pitch, formant frequencies)
    - ML models (gender classification from audio)
    - Voice characteristics
    
    For now, we use text-based hints and alternating assignment.
    """
    speaker_genders = {}
    
    # Gender indicators in text
    female_keywords = [
        "she", "her", "hers", "herself",
        "mrs", "ms", "miss", "ma'am", "madam",
        "lady", "woman", "women", "girl", "girls",
        "mother", "mom", "sister", "daughter", "wife",
        "actress", "queen", "princess"
    ]
    
    male_keywords = [
        "he", "him", "his", "himself",
        "mr", "sir", "gentleman",
        "man", "men", "boy", "boys",
        "father", "dad", "brother", "son", "husband",
        "actor", "king", "prince"
    ]
    
    speaker_ids = sorted(speaker_stats.keys())
    
    for speaker_id in speaker_ids:
        # Analyze text for gender clues
        all_text = " ".join(speaker_stats[speaker_id]['texts']).lower()
        
        female_score = sum(1 for keyword in female_keywords if keyword in all_text)
        male_score = sum(1 for keyword in male_keywords if keyword in all_text)
        
        if female_score > male_score:
            gender = "female"
        elif male_score > female_score:
            gender = "male"
        else:
            # No clear indicators - alternate by speaker number
            speaker_num = int(speaker_id.split("_")[1])
            gender = "female" if speaker_num % 2 == 1 else "male"
        
        speaker_genders[speaker_id] = gender
        print(f"{speaker_id}: {gender} (F:{female_score}, M:{male_score})")
    
    return speaker_genders


def process_speaker_diarization(transcript_data: Dict) -> Tuple[List[Dict], Dict[str, str]]:
    """
    Complete speaker diarization pipeline.
    
    Args:
        transcript_data: Transcript with segments from Groq Whisper
    
    Returns:
        Tuple of:
        - List of segments with speaker IDs
        - Dict mapping speaker IDs to genders
    """
    print("\n" + "=" * 60)
    print("SPEAKER DIARIZATION")
    print("=" * 60)
    
    segments = transcript_data.get('segments', [])
    
    if not segments:
        print("No segments found in transcript")
        return [], {}
    
    # Step 1: Detect speaker changes
    print("\n1. Detecting speaker changes...")
    speaker_segments = detect_speaker_changes(segments, silence_threshold=0.8)
    
    # Step 2: Merge consecutive segments from same speaker
    print("\n2. Merging consecutive speaker segments...")
    merged_segments = merge_consecutive_speaker_segments(speaker_segments)
    
    # Step 3: Analyze speaker patterns
    print("\n3. Analyzing speaker patterns...")
    speaker_stats = analyze_speaker_patterns(merged_segments)
    
    for speaker, stats in speaker_stats.items():
        print(f"  {speaker}: {stats['segment_count']} turns, "
              f"{stats['total_duration']:.1f}s, "
              f"{stats['total_words']} words")
    
    # Step 4: Detect genders
    print("\n4. Detecting speaker genders...")
    speaker_genders = detect_speaker_genders(speaker_stats)
    
    print("\n" + "=" * 60)
    print(f"Identified {len(speaker_genders)} speakers")
    for speaker, gender in speaker_genders.items():
        print(f"  {speaker}: {gender}")
    print("=" * 60 + "\n")
    
    return merged_segments, speaker_genders


def refine_speaker_segments_with_words(segments: List[Dict]) -> List[Dict]:
    """
    Refine speaker segment boundaries using word-level timestamps.
    More accurate than segment-level timestamps.
    """
    refined = []
    
    for segment in segments:
        if 'words' in segment and segment['words']:
            # Use word-level timestamps for precise boundaries
            first_word = segment['words'][0]
            last_word = segment['words'][-1]
            
            refined_segment = segment.copy()
            refined_segment['start'] = first_word.get('start', segment['start'])
            refined_segment['end'] = last_word.get('end', segment['end'])
            refined.append(refined_segment)
        else:
            refined.append(segment)
    
    return refined

