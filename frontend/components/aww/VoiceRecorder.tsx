'use client';
import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Mic, Square, Send, RotateCcw } from 'lucide-react';

interface VoiceRecorderProps {
  onSubmit: (blob: Blob) => Promise<void>;
  loading?: boolean;
}

type RecordState = 'idle' | 'recording' | 'recorded';

export function VoiceRecorder({ onSubmit, loading }: VoiceRecorderProps) {
  const [state, setState] = useState<RecordState>('idle');
  const [seconds, setSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const blobRef = useRef<Blob | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      chunksRef.current = [];
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        blobRef.current = blob;
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach(t => t.stop());
      };
      mr.start();
      mediaRef.current = mr;
      setState('recording');
      setSeconds(0);
      timerRef.current = setInterval(() => setSeconds(s => s + 1), 1000);
    } catch {
      alert('Microphone access is required to record observations.');
    }
  };

  const stopRecording = () => {
    if (mediaRef.current) {
      mediaRef.current.stop();
      if (timerRef.current) clearInterval(timerRef.current);
      setState('recorded');
    }
  };

  const reset = () => {
    setState('idle');
    setSeconds(0);
    setAudioUrl(null);
    blobRef.current = null;
  };

  const submit = async () => {
    if (blobRef.current) await onSubmit(blobRef.current);
  };

  const fmt = (s: number) => `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`;

  return (
    <div className="flex flex-col items-center gap-6 py-8">
      {state === 'idle' && (
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="h-24 w-24 rounded-full bg-brand-50 border-2 border-brand-200 flex items-center justify-center">
              <Mic className="h-10 w-10 text-brand-600" />
            </div>
          </div>
          <p className="text-sm text-muted-foreground text-center max-w-xs">
            Tap to record your observation in any language
          </p>
          <Button onClick={startRecording} size="xl" className="gap-2">
            <Mic className="h-5 w-5" /> Start Recording
          </Button>
        </div>
      )}

      {state === 'recording' && (
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <div className="h-24 w-24 rounded-full bg-red-50 border-2 border-red-300 flex items-center justify-center recording-pulse">
              <Mic className="h-10 w-10 text-red-500" />
            </div>
            <div className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 border-2 border-white animate-pulse" />
          </div>
          <div className="text-2xl font-mono font-bold text-red-600">{fmt(seconds)}</div>
          <p className="text-sm text-muted-foreground">Recording… speak clearly</p>
          <Button onClick={stopRecording} variant="danger" size="xl" className="gap-2">
            <Square className="h-5 w-5" /> Stop Recording
          </Button>
        </div>
      )}

      {state === 'recorded' && (
        <div className="flex flex-col items-center gap-4 w-full max-w-sm">
          <div className="h-24 w-24 rounded-full bg-green-50 border-2 border-green-300 flex items-center justify-center">
            <Mic className="h-10 w-10 text-green-600" />
          </div>
          <p className="text-sm font-semibold text-green-700">Recording complete · {fmt(seconds)}</p>
          {audioUrl && (
            <audio controls src={audioUrl} className="w-full rounded-xl" />
          )}
          <div className="flex gap-3 w-full">
            <Button onClick={reset} variant="outline" className="flex-1 gap-2">
              <RotateCcw className="h-4 w-4" /> Re-record
            </Button>
            <Button onClick={submit} loading={loading} className="flex-1 gap-2">
              <Send className="h-4 w-4" /> Submit
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
