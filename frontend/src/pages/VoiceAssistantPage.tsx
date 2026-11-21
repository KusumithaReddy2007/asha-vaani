import React, { useState, useEffect, useRef } from 'react';
import { Microphone3D } from '../components/3d/Microphone3D';
import { WaveformVisualizer } from '../components/WaveformVisualizer';
import { ExtractedRecord, DetectedDangerSign } from '../types';
import { api } from '../services/api';
import {
  Mic,
  MicOff,
  RotateCcw,
  Volume2,
  CheckCircle2,
  AlertOctagon,
  Sparkles,
  Send,
  Languages,
  Radio,
  FileCheck,
  Check,
  MapPin,
  Home,
  Navigation,
} from 'lucide-react';

export const VoiceAssistantPage: React.FC = () => {
  // Voice State
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [language, setLanguage] = useState<'en' | 'hi' | 'kn'>('en');
  const [audioLevel, setAudioLevel] = useState(0);

  // Audio Context & Analyser
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);
  const finalTranscriptRef = useRef('');
  const submittedTranscriptRef = useRef(false);
  const wsRef = useRef<WebSocket | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);

  // Conversation & Extraction State
  const [transcript, setTranscript] = useState('');
  const [conversationHistory, setConversationHistory] = useState<
    Array<{ sender: 'user' | 'assistant' | 'system'; text: string; time: string }>
  >([
    {
      sender: 'assistant',
      text: 'Namaste! ASHA-VAANI is ready. Speak beneficiary details or visit notes in English, Hindi, or Kannada.',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [record, setRecord] = useState<ExtractedRecord>({
    vaccinations: {},
    health_observations: [],
    danger_signs: [],
    status: 'Pending Confirmation',
    confidence: 0.95,
  });

  const [activeDanger, setActiveDanger] = useState<DetectedDangerSign | null>(null);
  const [saveSuccessMessage, setSaveSuccessMessage] = useState<string | null>(null);
  const [manualText, setManualText] = useState('');

  // Live Location & House Number State
  const [houseNumber, setHouseNumber] = useState('');
  const [gpsLocation, setGpsLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [gpsStatus, setGpsStatus] = useState('Location not captured');

  const [liveLocation, setLiveLocation] = useState<{
    lat: number;
    lng: number;
    accuracy?: number;
    address: string;
    isLive: boolean;
  }>({
    lat: 12.9784,
    lng: 77.7289,
    accuracy: 6,
    address: 'Kadugodi Sector 4, Belathur Ward 3, Bengaluru Urban',
    isLive: false,
  });
  const [isCapturingLocation, setIsCapturingLocation] = useState(false);

  // Capture Live GPS Location
  const captureLiveLocation = () => {
    if (!('geolocation' in navigator)) {
      console.warn('Geolocation not supported by browser.');
      return;
    }
    setIsCapturingLocation(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = Number(pos.coords.latitude.toFixed(5));
        const lng = Number(pos.coords.longitude.toFixed(5));
        const acc = Math.round(pos.coords.accuracy);
        setLiveLocation({
          lat,
          lng,
          accuracy: acc,
          address: `Bengaluru (${lat}°, ${lng}°)`,
          isLive: true,
        });
        setGpsLocation({ latitude: lat, longitude: lng });
        setGpsStatus('Live GPS captured');
        setIsCapturingLocation(false);
      },
      (err) => {
        console.warn('Geolocation fallback:', err.message);
        setIsCapturingLocation(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  useEffect(() => {
    captureLiveLocation();
  }, []);

  // 1. Initialize WebSocket Connection
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/voice`;

    let ws: WebSocket;
    try {
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        ws.send(JSON.stringify({ type: 'init', language }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'tts_audio_ready') {
            playTimbreAudio(data.audio_base64);
          } else if (data.type === 'tts_fallback') {
            speakBrowserText(data.text);
          } else if (data.type === 'record_updated') {
            setRecord(data.record);
            if (data.record.house_number) {
              setHouseNumber(data.record.house_number);
            }
            setIsProcessing(false);

            if (data.readback_summary) {
              setConversationHistory((prev) => [
                ...prev,
                {
                  sender: 'assistant',
                  text: data.readback_summary,
                  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                },
              ]);
              // Trigger read-back TTS
              speakText(data.readback_summary);
            }
          } else if (data.type === 'danger_sign_detected') {
            const dangers: DetectedDangerSign[] = data.dangers;
            if (dangers.length > 0) {
              setActiveDanger(dangers[dangers.length - 1]);
              setConversationHistory((prev) => [
                ...prev,
                {
                  sender: 'system',
                  text: `EMERGENCY ALERT: ${dangers[dangers.length - 1].name} detected! Referral to PHC required.`,
                  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                },
              ]);
              speakText(data.spoken_alert || 'Emergency danger sign detected. Refer to PHC immediately.');
            }
          } else if (data.type === 'record_saved_successfully') {
            setRecord((prev) => ({ ...prev, status: 'Confirmed' }));
            setSaveSuccessMessage(data.message || 'Record confirmed and saved to database!');
            setIsProcessing(false);
            setConversationHistory((prev) => [
              ...prev,
              {
                sender: 'assistant',
                text: 'Record has been successfully saved to the database. Follow-up task added to calendar.',
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
            speakText('Record confirmed and saved successfully.');
          }
        } catch (e) {
          console.error('Error handling WS message:', e);
        }
      };

      ws.onclose = () => setWsConnected(false);
      ws.onerror = () => setWsConnected(false);
    } catch (e) {
      console.warn('WebSocket fallback mode active.');
    }

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [language]);

  // 2. Real Browser Microphone Access (Web Audio API)
  const startRealMicrophone = async () => {
    finalTranscriptRef.current = '';
    submittedTranscriptRef.current = false;
    setTranscript('');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 128;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      // Start level meter loop
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateLevel = () => {
        if (!analyserRef.current || !isListening) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
        const avg = sum / dataArray.length / 255.0;
        setAudioLevel(avg);
        requestAnimationFrame(updateLevel);
      };
      updateLevel();

      // Browser Web Speech Recognition for Real-time Transcription
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;
        recognition.continuous = true;
        recognition.interimResults = true;

        if (language === 'hi') recognition.lang = 'hi-IN';
        else if (language === 'kn') recognition.lang = 'kn-IN';
        else recognition.lang = 'en-IN';

        recognition.onresult = (event: any) => {
          let finalText = '';
          let interimText = '';

          // Collect the complete recognition results
          for (let i = 0; i < event.results.length; i++) {
            const result = event.results[i];
            const spokenText = result[0].transcript;

            if (result.isFinal) {
              finalText += spokenText + ' ';
            } else {
              interimText += spokenText + ' ';
            }
          }

          // Keep all final words until recording ends
          finalTranscriptRef.current = finalText.trim();

          // Show final and currently recognized words
          setTranscript(
            [finalText.trim(), interimText.trim()]
              .filter(Boolean)
              .join(' ')
          );
        };

        recognition.onerror = (e: any) => console.warn('Recognition event:', e);

        recognition.onend = () => {
          setIsListening(false);
          setAudioLevel(0);

          // Clean up microphone resources
          if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(track => track.stop());
            mediaStreamRef.current = null;
          }

          if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
          }

          // Submit the complete transcript only once
          const completeTranscript = finalTranscriptRef.current.trim();

          if (completeTranscript && !submittedTranscriptRef.current) {
            submittedTranscriptRef.current = true;
            handleSpeechSubmit(completeTranscript);
          }
        };

        recognition.start();
      }

      setIsListening(true);
    } catch (err) {
      console.error('Microphone access error:', err);
      // Fallback: still allow audio simulation
      setIsListening(true);
    }
  };

  const stopMicrophone = () => {
    setIsListening(false);
    setAudioLevel(0);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  const toggleRecording = () => {
    if (isListening) stopMicrophone();
    else startRealMicrophone();
  };

  // 3. Gnani Timbre v3.0 Audio Playback
  const playTimbreAudio = (audioBase64: string) => {
    try {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }

      const binary = atob(audioBase64);
      const bytes = new Uint8Array(binary.length);

      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }

      const blob = new Blob([bytes], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(blob);

      audioUrlRef.current = audioUrl;

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onplay = () => setIsSpeaking(true);

      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
        audioUrlRef.current = null;
        audioRef.current = null;
      };

      audio.onerror = () => {
        setIsSpeaking(false);
        console.error('Gnani audio playback failed.');
      };

      audio.play().catch((error) => {
        setIsSpeaking(false);
        console.error('Audio playback was blocked:', error);
      });
    } catch (error) {
      setIsSpeaking(false);
      console.error('Unable to decode Gnani audio:', error);
    }
  };

  // Browser speech is used only as a fallback.
  const speakBrowserText = (text: string) => {
    if (!('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang =
      language === 'hi' ? 'hi-IN' :
      language === 'kn' ? 'kn-IN' : 'en-IN';

    utterance.rate = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  // Request speech from Gnani Timbre v3.0.
  const speakText = (text: string) => {
    if (!text.trim()) return;

    const languageCode =
      language === 'hi' ? 'hi-IN' :
      language === 'kn' ? 'kn-IN' : 'en-IN';

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'request_tts',
        text,
        language_code: languageCode,
      }));
    } else {
      speakBrowserText(text);
    }
  };

  // 4. Handle Utterance Submit (Via Mic or Text)
  const handleSpeechSubmit = (text: string) => {
    if (!text.trim()) return;
    setIsProcessing(true);

    // Add to history
    setConversationHistory((prev) => [
      ...prev,
      {
        sender: 'user',
        text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);

    // Send over WebSocket or direct fallback
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'text_utterance',
          text,
          language,
        })
      );
    } else {
      // Direct REST evaluation fallback
      api.evaluateDanger(text, language).then((dangerRes) => {
        if (dangerRes.danger_detected && dangerRes.detections.length > 0) {
          setActiveDanger(dangerRes.detections[0]);
        }
        setIsProcessing(false);
      });
    }
    setTranscript('');
    setManualText('');
  };

  // 5. Explicit Record Confirmation
  const confirmAndSaveRecord = async () => {
    setIsProcessing(true);
    try {
      await api.saveConfirmedVisit({
        beneficiary_id_str: record.beneficiary_id || '',
        visit_type: record.visit_type || 'Household Visit',
        weight_kg: record.weight_kg,
        house_number: houseNumber.trim(),
        location_lat: gpsLocation?.latitude ?? null,
        location_lng: gpsLocation?.longitude ?? null,
        location_address: gpsLocation
          ? `${gpsLocation.latitude.toFixed(6)}, ${gpsLocation.longitude.toFixed(6)}`
          : '',
        vaccinations_given: record.vaccinations,
        health_observations: record.health_observations.join(', '),
        next_visit_date: record.next_visit_date,
        danger_signs_detected: record.danger_signs,
        referral_made: record.danger_signs.length > 0,
        transcript_snippet: record.raw_transcript,
      });

      setRecord((prev) => ({ ...prev, status: 'Confirmed' }));
      setSaveSuccessMessage('Record confirmed with GPS location and saved to database successfully!');
      speakText('Record confirmed and saved.');
    } catch (e: any) {
      console.error(e);
      alert('Error saving record: ' + e.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // 6. Reset Session
  const resetSession = () => {
    setRecord({
      vaccinations: {},
      health_observations: [],
      danger_signs: [],
      status: 'Pending Confirmation',
      confidence: 0.95,
    });
    setHouseNumber('');
    setActiveDanger(null);
    setSaveSuccessMessage(null);
    setTranscript('');
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'reset' }));
    }
  };

  // 7. Instant Demo Scenarios for Hackathon Presentation
  const triggerDemoScenario = (scenarioText: string) => {
    setTranscript(scenarioText);
    handleSpeechSubmit(scenarioText);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex flex-col gap-8">
      {/* Top Header & Mode Status */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-teal-500/20">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Live Healthcare Voice Assistant</h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold flex items-center gap-1.5 ${
                wsConnected
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
              }`}
            >
              <Radio className="w-3 h-3 animate-pulse" />
              {wsConnected ? 'Gnani WebSocket Live' : 'Voice Gateway Connected'}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Official Gnani Prisma v3.0 STT & Timbre v3.0 TTS pipeline with deterministic MoHFW danger sign safety.
          </p>
        </div>

        {/* Language Selection */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-emerald-950/60 border border-teal-500/30 backdrop-blur-md">
            <Languages className="w-4 h-4 text-[#00f5d4] ml-2" />
            <button
              onClick={() => setLanguage('en')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                language === 'en' ? 'bg-[#00f5d4] text-[#031410]' : 'text-slate-300 hover:text-white'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage('hi')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                language === 'hi' ? 'bg-[#00f5d4] text-[#031410]' : 'text-slate-300 hover:text-white'
              }`}
            >
              हिन्दी
            </button>
            <button
              onClick={() => setLanguage('kn')}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                language === 'kn' ? 'bg-[#00f5d4] text-[#031410]' : 'text-slate-300 hover:text-white'
              }`}
            >
              ಕನ್ನಡ
            </button>
          </div>

          <button
            onClick={resetSession}
            title="Reset Conversation"
            className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white border border-teal-500/30 transition-all"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Critical Danger Sign Warning Banner (if detected) */}
      {activeDanger && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-rose-950 via-red-900 to-rose-950 border-2 border-rose-500 animate-danger-pulse flex flex-col sm:flex-row items-center gap-5 justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-rose-500/30 border border-rose-400 flex items-center justify-center text-rose-300 shrink-0">
              <AlertOctagon className="w-8 h-8 animate-bounce text-rose-200" />
            </div>
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-500/40 text-white font-mono text-[10px] font-bold tracking-wider">
                EMERGENCY DANGER SIGN DETECTED
              </div>
              <h3 className="text-xl font-bold text-white mt-1">"{activeDanger.name}"</h3>
              <p className="text-xs text-rose-200 font-semibold mt-0.5">
                Immediate Action: {activeDanger.action_instruction}
              </p>
              <p className="text-[11px] text-rose-300/80 font-mono mt-1">
                Guideline: {activeDanger.guideline || 'MoHFW Protocol Section 4.1'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => speakText(activeDanger.spoken_instruction)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs border border-white/20"
            >
              <Volume2 className="w-4 h-4 text-rose-300" />
              Replay Audio
            </button>
            <button
              onClick={() => setActiveDanger(null)}
              className="px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs"
            >
              Acknowledge & Triage
            </button>
          </div>
        </div>
      )}

      {/* Main Grid: Left 3D Microphone & Audio, Right Structured Record */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* LEFT COLUMN: 3D Mic & Audio Controls (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          <div className="p-8 rounded-3xl glass-panel border border-teal-500/25 flex flex-col items-center justify-center relative overflow-hidden">
            {/* Background Radial Glow */}
            <div
              className={`absolute w-72 h-72 rounded-full blur-[100px] pointer-events-none transition-all duration-700 ${
                activeDanger
                  ? 'bg-rose-500/25'
                  : isListening
                  ? 'bg-[#00f5d4]/25'
                  : isProcessing
                  ? 'bg-amber-500/20'
                  : 'bg-teal-500/10'
              }`}
            />

            {/* Status Pills */}
            <div className="flex items-center gap-2 mb-4 z-10">
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 ${
                  isListening
                    ? 'bg-[#00f5d4]/20 text-[#00f5d4] border border-[#00f5d4]/40 shadow-[0_0_15px_rgba(0,245,212,0.3)] animate-pulse'
                    : isProcessing
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : isSpeaking
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'bg-white/5 text-slate-400 border border-white/10'
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    isListening
                      ? 'bg-[#00f5d4] animate-ping'
                      : isProcessing
                      ? 'bg-amber-400'
                      : isSpeaking
                      ? 'bg-emerald-400 animate-pulse'
                      : 'bg-slate-500'
                  }`}
                />
                {isListening
                  ? 'Listening to Microphone...'
                  : isProcessing
                  ? 'Processing with Gnani AI...'
                  : isSpeaking
                  ? 'ASHA-VAANI Reading Back Record...'
                  : 'Ready to Record'}
              </span>
            </div>

            {/* 3D Interactive Microphone Scene */}
            <div className="w-64 h-64 relative flex items-center justify-center z-10">
              <Microphone3D
                isListening={isListening}
                isProcessing={isProcessing}
                isSpeaking={isSpeaking}
                audioLevel={audioLevel}
              />
            </div>

            {/* Real-time Oscilloscope Waveform */}
            <div className="w-full mt-4 z-10">
              <WaveformVisualizer analyser={analyserRef.current} isActive={isListening} />
            </div>

            {/* Big Mic Toggle Button */}
            <div className="mt-6 flex items-center gap-4 z-10">
              <button
                onClick={toggleRecording}
                className={`flex items-center gap-3 px-8 py-4 rounded-2xl font-bold text-sm transition-all cursor-pointer ${
                  isListening
                    ? 'bg-rose-500 hover:bg-rose-600 text-white shadow-[0_0_30px_rgba(244,63,94,0.5)]'
                    : 'glass-button-neon text-[#031410] shadow-[0_0_35px_rgba(0,245,212,0.4)]'
                }`}
              >
                {isListening ? (
                  <>
                    <MicOff className="w-5 h-5" />
                    Stop Listening
                  </>
                ) : (
                  <>
                    <Mic className="w-5 h-5 text-[#031410]" />
                    Tap to Speak
                  </>
                )}
              </button>
            </div>

            {/* Interim Transcript preview */}
            {transcript && (
              <div className="mt-4 p-3 rounded-xl bg-teal-500/10 border border-teal-500/20 text-xs text-teal-200 font-mono w-full text-center z-10 animate-pulse">
                "{transcript}"
              </div>
            )}
          </div>

          {/* Quick 1-Click Demo Scenarios (Crucial for Hackathon Demonstration) */}
          <div className="p-6 rounded-2xl glass-panel border border-teal-500/20 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#00f5d4] flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                Hackathon Demo Scenarios (1-Click Test)
              </span>
              <span className="text-[10px] text-slate-400">Click to feed speech utterance</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <button
                onClick={() =>
                  triggerDemoScenario('Lakshmi, 10 days baby, weight 2.8 kilo, BCG given, next visit 20 November.')
                }
                className="p-3 rounded-xl bg-white/5 hover:bg-teal-500/15 border border-white/10 hover:border-teal-500/30 text-left text-xs transition-all"
              >
                <span className="font-bold text-white block">1. Normal Newborn Visit</span>
                <span className="text-[11px] text-slate-400">"Lakshmi, 10 days baby, weight 2.8 kilo, BCG given..."</span>
              </button>

              <button
                onClick={() =>
                  triggerDemoScenario('Priya, ANC checkup completed, weight 55 kg, IFA goli given, next visit 25 December.')
                }
                className="p-3 rounded-xl bg-white/5 hover:bg-teal-500/15 border border-white/10 hover:border-teal-500/30 text-left text-xs transition-all"
              >
                <span className="font-bold text-white block">2. Pregnancy Visit (ANC)</span>
                <span className="text-[11px] text-slate-400">"Priya, ANC checkup, weight 55 kg, IFA goli given..."</span>
              </button>

              <button
                onClick={() => triggerDemoScenario('No, weight is 2.8 kilo.')}
                className="p-3 rounded-xl bg-white/5 hover:bg-teal-500/15 border border-white/10 hover:border-teal-500/30 text-left text-xs transition-all"
              >
                <span className="font-bold text-white block">3. Voice Correction (Weight)</span>
                <span className="text-[11px] text-slate-400">"No, weight is 2.8 kilo." (Preserves record)</span>
              </button>

              <button
                onClick={() =>
                  triggerDemoScenario(
                    'Sunita Gowda, 8 months pregnant, has bleeding during pregnancy since morning!'
                  )
                }
                className="p-3 rounded-xl bg-rose-950/30 hover:bg-rose-950/50 border border-rose-500/30 text-left text-xs transition-all"
              >
                <span className="font-bold text-rose-300 block">4. Danger Sign: Bleeding</span>
                <span className="text-[11px] text-rose-200/70">"Sunita, bleeding during pregnancy..."</span>
              </button>

              <button
                onClick={() =>
                  triggerDemoScenario('10 days baby has high fever in newborn, body burning hot, not feeding!')
                }
                className="p-3 rounded-xl bg-rose-950/30 hover:bg-rose-950/50 border border-rose-500/30 text-left text-xs transition-all sm:col-span-2"
              >
                <span className="font-bold text-rose-300 block">5. Danger Sign: Newborn High Fever</span>
                <span className="text-[11px] text-rose-200/70">"10 days baby has high fever in newborn, hot body..."</span>
              </button>
            </div>
          </div>

          {/* Manual Text Fallback Input */}
          <div className="flex items-center gap-2 p-2 rounded-2xl glass-panel border border-teal-500/20">
            <input
              type="text"
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSpeechSubmit(manualText)}
              placeholder="Or type speech phrase in English / Hindi / Kannada..."
              className="w-full bg-transparent border-0 px-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none"
            />
            <button
              onClick={() => handleSpeechSubmit(manualText)}
              className="p-2.5 rounded-xl bg-[#00f5d4] hover:bg-teal-400 text-[#031410] font-bold transition-all cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: Structured Record & Voice Confirmation Gate (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="p-6 rounded-3xl glass-panel border border-teal-500/30 flex flex-col gap-5 relative">
            <div className="flex items-center justify-between pb-3 border-b border-teal-500/20">
              <div className="flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-[#00f5d4]" />
                <h3 className="font-bold text-white text-base">Structured Healthcare Record</h3>
              </div>
              <span
                className={`text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full ${
                  record.status === 'Confirmed'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                }`}
              >
                {record.status}
              </span>
            </div>

            {/* Success notification banner */}
            {saveSuccessMessage && (
              <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-200 text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                {saveSuccessMessage}
              </div>
            )}

            {/* Extracted Fields */}
            <div className="space-y-3.5 text-xs">
              {/* Beneficiary */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-slate-400">Beneficiary:</span>
                <span className="font-bold text-white font-mono">
                  {record.beneficiary_name ? (
                    record.beneficiary_id
                      ? `${record.beneficiary_name} (${record.beneficiary_id})`
                      : record.beneficiary_name
                  ) : (
                    <span className="text-slate-500 italic">Listening for name...</span>
                  )}
                </span>
              </div>

              {/* Visit Type */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-slate-400">Visit Type:</span>
                <span className="font-semibold text-teal-300">
                  {record.visit_type || <span className="text-slate-500 italic">Pending...</span>}
                </span>
              </div>

              {/* House Number (Manual Entry + Voice Extraction) */}
              <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5 font-medium">
                    <Home className="w-3.5 h-3.5 text-[#00f5d4]" />
                    House / Door Number:
                  </span>
                  <span className="text-[10px] text-teal-300 font-mono">
                    {houseNumber ? 'Custom / Verified' : 'Manual or voice'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={houseNumber}
                    onChange={(e) => setHouseNumber(e.target.value)}
                    placeholder="Enter house no. (e.g. #42/B, Belathur Ward 3)"
                    className="w-full bg-black/40 border border-teal-500/30 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#00f5d4] font-mono transition-all"
                  />
                </div>
              </div>

              {/* Live Location GPS Capture */}
              <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5 font-medium">
                    <MapPin className="w-3.5 h-3.5 text-[#00f5d4]" />
                    Live Visit Location:
                  </span>
                  <button
                    onClick={captureLiveLocation}
                    disabled={isCapturingLocation}
                    className="text-[10px] text-[#00f5d4] hover:underline flex items-center gap-1 font-mono transition-all cursor-pointer"
                  >
                    <Navigation className={`w-3 h-3 ${isCapturingLocation ? 'animate-spin' : ''}`} />
                    {isCapturingLocation ? 'Locating...' : 'Refresh GPS'}
                  </button>
                </div>
                <div className="flex items-center justify-between text-[11px] font-mono p-2 rounded-lg bg-teal-950/40 border border-teal-500/25">
                  <span className="text-white flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${liveLocation.isLive ? 'bg-emerald-400 animate-pulse' : 'bg-teal-400'}`} />
                    {liveLocation.lat.toFixed(4)}° N, {liveLocation.lng.toFixed(4)}° E
                  </span>
                  <span className="text-[10px] text-teal-300 font-semibold">
                    {liveLocation.isLive ? `Live GPS (±${liveLocation.accuracy}m)` : 'Kadugodi Sub-Centre'}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 truncate">
                  📍 {liveLocation.address}
                </span>
              </div>

              {/* Weight */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-slate-400">Recorded Weight:</span>
                <span className="font-bold text-[#00f5d4] font-mono text-sm">
                  {record.weight_kg ? `${record.weight_kg} kg` : <span className="text-slate-500 italic">Pending...</span>}
                </span>
              </div>

              {/* Vaccinations */}
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400">Vaccinations & Meds:</span>
                  <span className="text-[10px] text-teal-400 font-mono">
                    {Object.keys(record.vaccinations).length} logged
                  </span>
                </div>
                {Object.keys(record.vaccinations).length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(record.vaccinations).map(([vax, status]) => (
                      <span
                        key={vax}
                        className="px-2.5 py-1 rounded-lg bg-teal-500/20 text-teal-200 text-[11px] font-mono border border-teal-500/30 flex items-center gap-1.5"
                      >
                        <Check className="w-3 h-3 text-[#00f5d4]" />
                        {vax}: <strong className="text-white">{status}</strong>
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-slate-500 italic text-xs">No vaccinations logged in this session</span>
                )}
              </div>

              {/* Health Observations */}
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400">Health Observations:</span>
                  <span className="text-[10px] text-teal-400 font-mono">
                    {record.health_observations.length} recorded
                  </span>
                </div>

                {record.health_observations.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {record.health_observations.map((observation, index) => (
                      <span
                        key={`${observation}-${index}`}
                        className="px-2.5 py-1 rounded-lg bg-blue-500/20 text-blue-200 text-[11px] border border-blue-500/30"
                      >
                        {observation}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-slate-500 italic text-xs">
                    No health observations recorded
                  </span>
                )}
              </div>

              {/* Next Visit Date */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-slate-400">Next Scheduled Visit:</span>
                <span className="font-bold text-white font-mono">
                  {record.next_visit_date || <span className="text-slate-500 italic">Not set</span>}
                </span>
              </div>

              {/* Danger Signs Status */}
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Danger Signs:</span>
                  {record.danger_signs.length > 0 ? (
                    <span className="px-2 py-0.5 rounded bg-rose-500/30 text-rose-300 font-bold font-mono text-[10px]">
                      {record.danger_signs.length} DETECTED
                    </span>
                  ) : (
                    <span className="text-emerald-400 font-medium">None detected (Normal)</span>
                  )}
                </div>
              </div>
            </div>

            {/* Readback & Confirmation Gate Box */}
            <div className="mt-2 p-4 rounded-2xl bg-teal-950/40 border border-teal-500/30 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#00f5d4] flex items-center gap-1.5">
                  <Volume2 className="w-4 h-4" />
                  Confirmation Gate
                </span>
                <button
                  onClick={() =>
                    record.clarification_needed && speakText(record.clarification_needed)
                  }
                  className="text-[11px] text-teal-300 hover:text-white flex items-center gap-1 underline"
                >
                  Replay Summary
                </button>
              </div>

              <p className="text-xs text-slate-300 italic leading-relaxed">
                "{record.clarification_needed ||
                  'Speak beneficiary name and visit data to extract details and generate readback.'}"
              </p>

              {/* Confirm / Save Actions */}
              <div className="pt-2 flex items-center gap-2">
                <button
                  onClick={confirmAndSaveRecord}
                  disabled={record.status === 'Confirmed'}
                  className={`w-full py-3 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all ${
                    record.status === 'Confirmed'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 cursor-not-allowed'
                      : 'glass-button-neon text-[#031410] shadow-[0_0_20px_rgba(0,245,212,0.3)] cursor-pointer'
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  {record.status === 'Confirmed' ? 'Record Saved & Synced' : 'Confirm & Save Record'}
                </button>
              </div>
              <p className="text-[10px] text-center text-slate-400">
                Or speak: <em>"Yes, save it"</em> to confirm via voice
              </p>
            </div>
          </div>

          {/* Transcript Snippet History Box */}
          <div className="p-4 rounded-2xl glass-panel border border-teal-500/15 max-h-56 overflow-y-auto flex flex-col gap-2.5">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Session Conversation Log
            </span>
            {conversationHistory.map((msg, i) => (
              <div
                key={i}
                className={`p-2.5 rounded-xl text-xs ${
                  msg.sender === 'user'
                    ? 'bg-teal-500/15 text-teal-200 border border-teal-500/25 ml-4'
                    : msg.sender === 'system'
                    ? 'bg-rose-950/60 text-rose-300 border border-rose-500/40'
                    : 'bg-white/5 text-slate-300 mr-4'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] opacity-70 mb-0.5">
                  <span className="font-bold capitalize">{msg.sender}</span>
                  <span>{msg.time}</span>
                </div>
                <p>{msg.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};