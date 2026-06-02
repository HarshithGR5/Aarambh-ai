'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { childrenApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PageHeader } from '@/components/shared/PageHeader';
import { toast } from 'sonner';
import { UserPlus } from 'lucide-react';
import type { ChildCreate } from '@/lib/types';

const schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum(['MALE', 'FEMALE', 'OTHER']),
  parent_name: z.string().optional(),
  parent_phone: z.string().optional(),
  parent_language: z.string().default('hi'),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export default function RegisterChildPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const qc = useQueryClient();

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { gender: 'FEMALE', parent_language: 'hi' },
  });

  const mutation = useMutation({
    mutationFn: (data: ChildCreate) => childrenApi.create(data),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['children'] });
      toast.success(`${res.data.full_name} registered successfully!`);
      router.replace(`/children/${res.data.id}`);
    },
    onError: () => toast.error('Failed to register child. Please try again.'),
  });

  const onSubmit = (data: FormData) => {
    mutation.mutate({ ...data, awc_id: user?.awc_id ?? 1 });
  };

  return (
    <div className="space-y-5 animate-fade-in">
      <PageHeader title="Register Child" backHref="/children" />

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Card>
          <CardHeader><CardTitle className="text-base">Child Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Full Name *</Label>
              <Input placeholder="Child's full name" {...register('full_name')} />
              {errors.full_name && <p className="text-xs text-destructive">{errors.full_name.message}</p>}
            </div>

            <div className="space-y-2">
              <Label>Date of Birth *</Label>
              <Input type="date" max={new Date().toISOString().split('T')[0]} {...register('date_of_birth')} />
              {errors.date_of_birth && <p className="text-xs text-destructive">{errors.date_of_birth.message}</p>}
            </div>

            <div className="space-y-2">
              <Label>Gender *</Label>
              <Select onValueChange={(v) => setValue('gender', v as 'MALE' | 'FEMALE' | 'OTHER')} defaultValue="FEMALE">
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="FEMALE">Girl (Female)</SelectItem>
                  <SelectItem value="MALE">Boy (Male)</SelectItem>
                  <SelectItem value="OTHER">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Parent / Guardian</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Parent Name</Label>
              <Input placeholder="Mother's or father's name" {...register('parent_name')} />
            </div>
            <div className="space-y-2">
              <Label>WhatsApp Number</Label>
              <Input type="tel" placeholder="10-digit phone number" {...register('parent_phone')} />
            </div>
            <div className="space-y-2">
              <Label>Preferred Language</Label>
              <Select onValueChange={(v) => setValue('parent_language', v)} defaultValue="hi">
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="hi">Hindi</SelectItem>
                  <SelectItem value="kn">Kannada</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="mr">Marathi</SelectItem>
                  <SelectItem value="ta">Tamil</SelectItem>
                  <SelectItem value="te">Telugu</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Additional Notes</CardTitle></CardHeader>
          <CardContent>
            <Input placeholder="Any relevant health or family notes…" {...register('notes')} />
          </CardContent>
        </Card>

        <Button type="submit" className="w-full gap-2" size="lg" loading={mutation.isPending}>
          <UserPlus className="h-5 w-5" /> Register Child
        </Button>
      </form>
    </div>
  );
}
