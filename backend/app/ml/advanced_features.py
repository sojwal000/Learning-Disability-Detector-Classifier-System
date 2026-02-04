"""
Advanced Feature Extraction from Audio and Handwriting
"""
import numpy as np
import librosa
import cv2
from typing import Dict, List, Tuple, Optional
import soundfile as sf

def extract_audio_features(audio_path: str) -> Dict:
    """
    Extract comprehensive audio features for dyslexia detection
    
    Features extracted:
    - MFCC (Mel-frequency cepstral coefficients)
    - Pitch/F0 (fundamental frequency)
    - Spectral features (centroid, rolloff, contrast)
    - Rhythm features (tempo, beat strength)
    - Energy and zero-crossing rate
    - Pause detection and fluency metrics
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Dictionary of extracted features
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # 1. MFCC Features (speech characteristics)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfccs, axis=1).tolist()
        mfcc_std = np.std(mfccs, axis=1).tolist()
        
        # 2. Pitch/F0 extraction
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        pitch_mean = float(np.mean(pitch_values)) if pitch_values else 0.0
        pitch_std = float(np.std(pitch_values)) if pitch_values else 0.0
        pitch_range = float(max(pitch_values) - min(pitch_values)) if pitch_values else 0.0
        
        # 3. Spectral Features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        
        # 4. Rhythm Features
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_strength = librosa.feature.tempogram(y=y, sr=sr)
        
        # 5. Energy Features
        rms_energy = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        
        # 6. Pause Detection (silence detection)
        intervals = librosa.effects.split(y, top_db=30)
        n_pauses = len(intervals) - 1 if len(intervals) > 0 else 0
        
        # Calculate pause durations
        pause_durations = []
        for i in range(len(intervals) - 1):
            pause_start = intervals[i][1]
            pause_end = intervals[i + 1][0]
            pause_duration = (pause_end - pause_start) / sr
            pause_durations.append(pause_duration)
        
        avg_pause_duration = float(np.mean(pause_durations)) if pause_durations else 0.0
        
        # 7. Speaking Rate
        speaking_time = sum([(end - start) / sr for start, end in intervals])
        speaking_rate = len(intervals) / duration if duration > 0 else 0.0
        
        # 8. Jitter and Shimmer (voice quality)
        frame_length = 2048
        hop_length = 512
        frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
        frame_energies = np.sum(frames ** 2, axis=0)
        
        jitter = float(np.std(np.diff(frame_energies))) if len(frame_energies) > 1 else 0.0
        shimmer = float(np.mean(np.abs(np.diff(frame_energies)))) if len(frame_energies) > 1 else 0.0
        
        # 9. Mel spectrogram features
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
        mel_mean = np.mean(mel_spectrogram, axis=1)[:10].tolist()
        
        # Compile all features
        features = {
            # Basic info
            "duration": float(duration),
            "sample_rate": int(sr),
            
            # MFCC
            "mfcc_mean": mfcc_mean,
            "mfcc_std": mfcc_std,
            
            # Pitch
            "pitch_mean": pitch_mean,
            "pitch_std": pitch_std,
            "pitch_range": pitch_range,
            
            # Spectral
            "spectral_centroid_mean": float(np.mean(spectral_centroids)),
            "spectral_centroid_std": float(np.std(spectral_centroids)),
            "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
            "spectral_rolloff_std": float(np.std(spectral_rolloff)),
            "spectral_contrast_mean": np.mean(spectral_contrast, axis=1).tolist(),
            
            # Rhythm
            "tempo": float(tempo),
            "beat_strength_mean": float(np.mean(beat_strength)),
            
            # Energy
            "rms_energy_mean": float(np.mean(rms_energy)),
            "rms_energy_std": float(np.std(rms_energy)),
            "zero_crossing_rate_mean": float(np.mean(zcr)),
            
            # Fluency
            "n_pauses": int(n_pauses),
            "avg_pause_duration": avg_pause_duration,
            "speaking_rate": float(speaking_rate),
            "speaking_time": float(speaking_time),
            
            # Voice quality
            "jitter": jitter,
            "shimmer": shimmer,
            
            # Mel features
            "mel_mean": mel_mean
        }
        
        return features
        
    except Exception as e:
        print(f"Error extracting audio features: {str(e)}")
        return {"error": str(e)}


def extract_handwriting_features(image_path: str) -> Dict:
    """
    Extract comprehensive handwriting features for dysgraphia detection
    
    Features extracted:
    - Edge and contour analysis
    - Letter spacing and alignment
    - Stroke consistency
    - Pressure patterns (from thickness)
    - Slant and baseline analysis
    - Size consistency
    
    Args:
        image_path: Path to handwriting image
        
    Returns:
        Dictionary of extracted features
    """
    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Could not load image"}
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # 1. Preprocessing
        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Adaptive thresholding for better text extraction
        binary = cv2.adaptiveThreshold(
            filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # 2. Edge Detection
        edges = cv2.Canny(binary, 50, 150)
        edge_density = float(np.sum(edges > 0) / (height * width))
        
        # 3. Contour Analysis
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter small contours (noise)
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 50]
        n_contours = len(contours)
        
        # Contour properties
        contour_areas = [cv2.contourArea(cnt) for cnt in contours]
        contour_perimeters = [cv2.arcLength(cnt, True) for cnt in contours]
        
        avg_contour_area = float(np.mean(contour_areas)) if contour_areas else 0.0
        std_contour_area = float(np.std(contour_areas)) if contour_areas else 0.0
        
        # 4. Bounding Box Analysis (letter size and spacing)
        bounding_boxes = [cv2.boundingRect(cnt) for cnt in contours]
        
        # Extract widths and heights
        widths = [w for _, _, w, h in bounding_boxes]
        heights = [h for _, _, w, h in bounding_boxes]
        
        avg_width = float(np.mean(widths)) if widths else 0.0
        std_width = float(np.std(widths)) if widths else 0.0
        avg_height = float(np.mean(heights)) if heights else 0.0
        std_height = float(np.std(heights)) if heights else 0.0
        
        # Size consistency
        size_consistency = 1.0 - (std_height / avg_height) if avg_height > 0 else 0.0
        
        # 5. Horizontal Spacing Analysis
        sorted_boxes = sorted(bounding_boxes, key=lambda x: x[0])  # Sort by x-coordinate
        spacings = []
        for i in range(len(sorted_boxes) - 1):
            x1, _, w1, _ = sorted_boxes[i]
            x2, _, _, _ = sorted_boxes[i + 1]
            spacing = x2 - (x1 + w1)
            if spacing > 0:  # Only positive spacings
                spacings.append(spacing)
        
        avg_spacing = float(np.mean(spacings)) if spacings else 0.0
        std_spacing = float(np.std(spacings)) if spacings else 0.0
        spacing_consistency = 1.0 - (std_spacing / avg_spacing) if avg_spacing > 0 else 0.0
        
        # 6. Vertical Alignment (baseline analysis)
        y_positions = [y for _, y, _, _ in bounding_boxes]
        avg_y = float(np.mean(y_positions)) if y_positions else 0.0
        std_y = float(np.std(y_positions)) if y_positions else 0.0
        alignment_quality = 1.0 - (std_y / height) if height > 0 else 0.0
        
        # 7. Stroke Thickness Analysis
        # Dilate to connect broken strokes
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Distance transform to find thickness
        dist_transform = cv2.distanceTransform(dilated, cv2.DIST_L2, 5)
        stroke_thickness = dist_transform[dist_transform > 0]
        
        avg_thickness = float(np.mean(stroke_thickness)) if len(stroke_thickness) > 0 else 0.0
        std_thickness = float(np.std(stroke_thickness)) if len(stroke_thickness) > 0 else 0.0
        thickness_consistency = 1.0 - (std_thickness / avg_thickness) if avg_thickness > 0 else 0.0
        
        # 8. Slant Analysis (using moments)
        slants = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 100:  # Only larger contours
                moments = cv2.moments(cnt)
                if moments['mu02'] != 0:
                    slant = moments['mu11'] / moments['mu02']
                    slants.append(slant)
        
        avg_slant = float(np.mean(slants)) if slants else 0.0
        std_slant = float(np.std(slants)) if slants else 0.0
        
        # 9. Texture Features (using GLCM-like analysis)
        # Simplified texture analysis
        dx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        dy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(dx**2 + dy**2)
        texture_energy = float(np.mean(gradient_magnitude))
        
        # 10. Aspect Ratios
        aspect_ratios = [w/h if h > 0 else 0 for _, _, w, h in bounding_boxes]
        avg_aspect_ratio = float(np.mean(aspect_ratios)) if aspect_ratios else 0.0
        
        # Compile all features
        features = {
            # Image properties
            "image_width": int(width),
            "image_height": int(height),
            
            # Edge and contour
            "edge_density": edge_density,
            "n_contours": int(n_contours),
            "avg_contour_area": avg_contour_area,
            "std_contour_area": std_contour_area,
            
            # Size features
            "avg_width": avg_width,
            "std_width": std_width,
            "avg_height": avg_height,
            "std_height": std_height,
            "size_consistency": float(size_consistency),
            "avg_aspect_ratio": avg_aspect_ratio,
            
            # Spacing features
            "avg_spacing": avg_spacing,
            "std_spacing": std_spacing,
            "spacing_consistency": float(spacing_consistency),
            
            # Alignment features
            "avg_y_position": avg_y,
            "std_y_position": std_y,
            "alignment_quality": float(alignment_quality),
            
            # Stroke features
            "avg_thickness": avg_thickness,
            "std_thickness": std_thickness,
            "thickness_consistency": float(thickness_consistency),
            
            # Slant features
            "avg_slant": avg_slant,
            "std_slant": std_slant,
            
            # Texture
            "texture_energy": texture_energy
        }
        
        return features
        
    except Exception as e:
        print(f"Error extracting handwriting features: {str(e)}")
        return {"error": str(e)}


def get_feature_vector_from_audio(audio_features: Dict) -> np.ndarray:
    """Convert audio features dict to numpy array for ML model"""
    if "error" in audio_features:
        return np.zeros(50)  # Return zero vector on error
    
    feature_list = [
        audio_features["duration"],
        audio_features["pitch_mean"],
        audio_features["pitch_std"],
        audio_features["pitch_range"],
        audio_features["spectral_centroid_mean"],
        audio_features["spectral_centroid_std"],
        audio_features["spectral_rolloff_mean"],
        audio_features["spectral_rolloff_std"],
        audio_features["tempo"],
        audio_features["beat_strength_mean"],
        audio_features["rms_energy_mean"],
        audio_features["rms_energy_std"],
        audio_features["zero_crossing_rate_mean"],
        audio_features["n_pauses"],
        audio_features["avg_pause_duration"],
        audio_features["speaking_rate"],
        audio_features["speaking_time"],
        audio_features["jitter"],
        audio_features["shimmer"],
    ]
    
    # Add MFCC means and stds
    feature_list.extend(audio_features["mfcc_mean"])
    feature_list.extend(audio_features["mfcc_std"])
    
    return np.array(feature_list)


def get_feature_vector_from_handwriting(hw_features: Dict) -> np.ndarray:
    """Convert handwriting features dict to numpy array for ML model"""
    if "error" in hw_features:
        return np.zeros(20)  # Return zero vector on error
    
    feature_list = [
        hw_features["edge_density"],
        hw_features["n_contours"],
        hw_features["avg_contour_area"],
        hw_features["std_contour_area"],
        hw_features["avg_width"],
        hw_features["std_width"],
        hw_features["avg_height"],
        hw_features["std_height"],
        hw_features["size_consistency"],
        hw_features["avg_aspect_ratio"],
        hw_features["avg_spacing"],
        hw_features["std_spacing"],
        hw_features["spacing_consistency"],
        hw_features["avg_y_position"],
        hw_features["std_y_position"],
        hw_features["alignment_quality"],
        hw_features["avg_thickness"],
        hw_features["std_thickness"],
        hw_features["thickness_consistency"],
        hw_features["texture_energy"],
    ]
    
    return np.array(feature_list)
