'use client';
import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { ImagePlus, X, Upload, Pencil } from 'lucide-react';
import Image from 'next/image';

const DRAWING_CONTEXTS = [
  { value: 'free_drawing',   label: 'Free Drawing' },
  { value: 'draw_a_person',  label: 'Draw a Person' },
  { value: 'family',         label: 'Family Drawing' },
  { value: 'house',          label: 'Draw a House' },
  { value: 'animal',         label: 'Draw an Animal' },
];

interface DrawingUploadProps {
  onUpload: (file: File, context: string) => Promise<void>;
  loading?: boolean;
}

export function DrawingUpload({ onUpload, loading }: DrawingUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [context, setContext] = useState('free_drawing');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f && f.type.startsWith('image/')) handleFile(f);
  };

  const submit = async () => {
    if (file) await onUpload(file, context);
  };

  return (
    <div className="space-y-5">
      <div>
        <Label className="mb-2 block">Drawing Type</Label>
        <Select value={context} onValueChange={setContext}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {DRAWING_CONTEXTS.map(c => (
              <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div
        className={cn(
          'relative border-2 border-dashed rounded-2xl transition-colors cursor-pointer',
          'hover:border-brand-400 hover:bg-brand-50/30',
          preview ? 'border-brand-300 bg-brand-50/20' : 'border-border bg-muted/30'
        )}
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
        />

        {preview ? (
          <div className="relative">
            <div className="relative aspect-square w-full overflow-hidden rounded-2xl">
              <Image src={preview} alt="Drawing preview" fill className="object-contain" />
            </div>
            <button
              onClick={e => { e.stopPropagation(); setFile(null); setPreview(null); }}
              className="absolute top-2 right-2 h-8 w-8 rounded-full bg-background border shadow-sm flex items-center justify-center hover:bg-destructive hover:text-white transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 py-12 px-4">
            <div className="h-16 w-16 rounded-2xl bg-brand-100 flex items-center justify-center">
              <ImagePlus className="h-8 w-8 text-brand-600" />
            </div>
            <div className="text-center">
              <p className="font-semibold text-foreground">Upload Drawing</p>
              <p className="text-sm text-muted-foreground mt-1">Tap to take photo or choose from gallery</p>
            </div>
          </div>
        )}
      </div>

      {file && (
        <Button onClick={submit} loading={loading} className="w-full gap-2" size="lg">
          <Upload className="h-5 w-5" />
          Upload & Analyze Drawing
        </Button>
      )}
    </div>
  );
}
