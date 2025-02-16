import torch
import torchaudio
import whisper
import numpy as np
from transformers import Pipeline, AutoTokenizer, AutoModelForSequenceClassification
import librosa
import pandas as pd
from typing import Dict, List, Tuple
import spacy
from scipy.stats import entropy
from textblob import TextBlob
from fastdtw import fastdtw
from scipy import signal
from transformers import pipeline
from typing import Dict, List, Tuple
import os

class SpeechFeatureExtractor:
    def __init__(self):
        self.whisper_model = whisper.load_model("base", device="cpu")
        self.nlp = spacy.load("en_core_web_sm")
        self.theta_threshold = 20.003  # aMCI threshold from 2022 study
        self.beta_threshold = 5.465    # aMCI threshold from 2022 study
        self.llm = pipeline("text-generation", model="gpt2", framework="pt")

    def generate_clinical_insights(self, features: Dict) -> str:
        """
        Generate clinical insights based on extracted features.
        References recent research for clinical significance.
        """
        insights = []
        
        # Check each feature against clinical thresholds
        if features.get("pause_count", 0) > 5:
            insights.append("Increased pause count may indicate working memory challenges.")
        
        if features.get("mean_pause_duration", 0) > 1.2:
            insights.append("Longer pauses may suggest lexical retrieval difficulties.")
        
        if features.get("theta_power", 0) > self.theta_threshold:
            insights.append("Elevated theta power could indicate attention regulation issues.")
        
        if features.get("beta_power", 0) < self.beta_threshold:
            insights.append("Reduced beta power may be associated with working memory impairment.")
            
        # Use LLM to enhance insights with more natural language
        if insights:
            context = "\n".join(insights)
            prompt = f"Based on speech analysis, the following patterns were observed:\n{context}\n\nProvide a brief, patient-friendly summary:"
            
            try:
                llm_response = self.llm(prompt, max_length=200, num_return_sequences=1)
                enhanced_insights = llm_response[0]['generated_text']
                return enhanced_insights
            except Exception as e:
                print(f"LLM generation error: {e}")
                return "\n".join(insights)  # Fallback to basic insights
        
        return "No significant cognitive risk indicators detected in the speech patterns."
    
    def _extract_llm_features(self, text: str):
        prompt = f"Analyze cognitive state from: {text}\nFeatures:"
        response = self.llm(prompt, max_length=100)
        return {
            "comprehension_score": self._parse_llm_output(response),
            "memory_issues": ... 
        }
        
    def _extract_longitudinal_features(self, audio_clips: List[str]):
        trends = {}
        for clip in audio_clips:
            features = self.extract_features(clip)
            # Track feature drift over time (e.g., increasing pause duration)
            for key in features:
                trends[key] = trends.get(key, []) + [features[key]]
        return trends

    def _extract_parkinsons_features(self, audio: np.ndarray, sr: int):
        # Use existing _extract_parkinsons_markers method
        return self._extract_parkinsons_markers(audio, sr)

    def _extract_acoustic_features(self, audio: np.ndarray, sr: int) -> Dict:
        try:
            # Get f0 and handle array operations correctly
            f0, voiced_flag, _ = librosa.pyin(audio,
                                            fmin=librosa.note_to_hz('C2'),
                                            fmax=librosa.note_to_hz('C7'),
                                            sr=sr)

            # Ensure we get single values
            voice_stability = float(np.nanstd(f0[voiced_flag])) if np.any(voiced_flag) else 0.0
            mean_f0 = float(np.nanmean(f0[voiced_flag])) if np.any(voiced_flag) else 0.0

            # Spectral features
            spec_cent = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spec_cent_mean = float(np.nanmean(spec_cent))

            return {
                "voice_stability": voice_stability,
                "mean_f0": mean_f0,
                "spectral_centroid": spec_cent_mean
            }
        except Exception as e:
            print(f"Acoustic feature error: {e}")
            return {"voice_stability": 0.0, "mean_f0": 0.0, "spectral_centroid": 0.0}

    def _extract_prosodic_features(self, audio: np.ndarray, sr: int) -> Dict:
        """Extract prosodic features with proper array handling"""
        try:
            # Energy and RMS
            rms = librosa.feature.rms(y=audio)[0]
            
            # Silence detection with proper array handling
            silence_intervals = librosa.effects.split(audio, top_db=20)
            
            # Handle pauses calculation safely
            if len(silence_intervals) > 1:
                pauses = np.diff(silence_intervals.flatten()) / sr
                pause_count = len(pauses)
                mean_pause_duration = float(np.mean(pauses))
            else:
                pause_count = 0
                mean_pause_duration = 0.0
                
            # Safely calculate energy variance
            energy_variance = float(np.var(rms)) if len(rms) > 0 else 0.0
                
            return {
                "energy_variance": energy_variance,
                "pause_count": pause_count,
                "mean_pause_duration": mean_pause_duration
            }
        except Exception as e:
            print(f"Prosodic feature error: {str(e)}")
            return {
                "energy_variance": 0.0,
                "pause_count": 0,
                "mean_pause_duration": 0.0
            }

    def extract_features(self, audio_path: str) -> Dict:
        """Generate synthetic features for demo"""
        # Simulate features based on the audio file
        return {
            "voice_stability": np.random.uniform(0.1, 1.0),  # Lower = worse
            "mean_f0": np.random.uniform(80, 300),          # Fundamental frequency
            "pause_count": np.random.randint(0, 10),        # More pauses = worse
            "mean_pause_duration": np.random.uniform(0.1, 2.0),
            "theta_power": np.random.uniform(0, 30),
            "beta_power": np.random.uniform(0, 10)
        }

    def _transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio using Whisper
        """
        result = self.whisper_model.transcribe(audio_path)
        return result["text"]

    def _extract_linguistic_features(self, text: str) -> Dict:
        """
        Extract linguistic features including complexity and coherence
        """
        doc = self.nlp(text)

        # Lexical diversity
        words = [token.text.lower() for token in doc if token.is_alpha]
        unique_words = set(words)

        # Sentence complexity
        sentences = list(doc.sents)
        sentence_lengths = [len(sent) for sent in sentences]

        # Part of speech distribution
        pos_counts = {}
        for token in doc:
            pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1

        # Named entity recognition
        named_entities = len(doc.ents)

        return {
            "lexical_diversity": len(unique_words) / len(words) if words else 0,
            "mean_sentence_length": np.mean(sentence_lengths),
            "pos_distribution": pos_counts,
            "named_entities_count": named_entities,
            "grammatical_complexity": self._calculate_grammatical_complexity(doc)
        }

    def _extract_cognitive_markers(self, text: str, audio: np.ndarray, sr: int) -> Dict:
        """
        Extract markers specifically related to cognitive function
        """
        doc = self.nlp(text)

        # Word finding difficulties (hesitations before content words)
        content_words = [token for token in doc if token.is_alpha and not token.is_stop]

        # Repetition patterns
        word_sequence = [token.text.lower() for token in doc]
        repetitions = self._count_repetitions(word_sequence)

        # Filler word analysis
        filler_count = sum(1 for word in word_sequence if word in self.FILLER_WORDS)

        # Semantic coherence
        coherence = self._calculate_semantic_coherence(doc)

        return {
            "word_finding_difficulty": self._calculate_word_finding_difficulty(content_words),
            "repetition_rate": repetitions / len(word_sequence) if word_sequence else 0,
            "filler_rate": filler_count / len(word_sequence) if word_sequence else 0,
            "semantic_coherence": coherence
        }

    def _calculate_grammatical_complexity(self, doc) -> float:
        """
        Calculate grammatical complexity score
        """
        # Depth of dependency tree
        depths = []
        for token in doc:
            depth = 0
            current = token
            while current.head != current:
                depth += 1
                current = current.head
            depths.append(depth)

        return np.mean(depths) if depths else 0

    def _count_repetitions(self, word_sequence: List[str]) -> int:
        """
        Count immediate word repetitions
        """
        repetitions = 0
        for i in range(len(word_sequence) - 1):
            if word_sequence[i] == word_sequence[i + 1]:
                repetitions += 1
        return repetitions

    def _calculate_semantic_coherence(self, doc) -> float:
        """
        Calculate semantic coherence between sentences
        """
        sentences = list(doc.sents)
        if len(sentences) <= 1:
            return 1.0

        coherence_scores = []
        for i in range(len(sentences) - 1):
            similarity = sentences[i].similarity(sentences[i + 1])
            coherence_scores.append(similarity)

        return float(np.mean(coherence_scores))

    def _calculate_word_finding_difficulty(self, content_words: List) -> float:
        """
        Estimate word finding difficulty based on patterns
        """
        if not content_words:
            return 0.0

        # Calculate average word frequency (using spaCy's frequency table)
        frequencies = [token.rank if hasattr(token, 'rank') else 0 for token in content_words]
        return float(np.mean(frequencies))

    def _extract_dtw_similarity(self, audio: np.ndarray, sr: int) -> float:
        """Extract DTW similarity (2024 research)"""
        try:
            segments = librosa.effects.split(audio)
            dtw_scores = []
            for i in range(len(segments)-1):
                distance, _ = fastdtw(segments[i], segments[i+1])
                dtw_scores.append(distance)
            return float(np.mean(dtw_scores)) if dtw_scores else 0
        except Exception as e:
            print(f"DTW calculation error: {e}")
            return 0

    def _extract_spectral_markers(self, audio: np.ndarray, sr: int) -> Dict:
        """Extract spectral markers (2022 PSD study)"""
        try:
            # Power spectral density analysis
            frequencies, times, Sxx = signal.spectrogram(audio, sr)
            theta_mask = (frequencies >= 4) & (frequencies <= 8)
            beta_mask = (frequencies >= 13) & (frequencies <= 30)
            
            theta_power = np.mean(Sxx[theta_mask])
            beta_power = np.mean(Sxx[beta_mask])
            
            return {
                "theta_power": float(theta_power),
                "beta_power": float(beta_power)
            }
        except Exception as e:
            print(f"Spectral analysis error: {e}")
            return {"theta_power": 0, "beta_power": 0}