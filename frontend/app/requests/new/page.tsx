'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { requestsApi } from '@/lib/api-client';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewRequestPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await requestsApi.create(formData);
      
      // Trigger classification
      if (response.request_id) {
        try {
          await requestsApi.classify(response.request_id);
        } catch (classifyError) {
          console.error('Classification failed:', classifyError);
          // Continue anyway - classification can happen later
        }
      }
      
      router.push(`/requests/${response.request_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create request');
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <Link
        href="/requests"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to requests
      </Link>

      <Card>
        <CardHeader>
          <CardTitle>Submit New Request</CardTitle>
          <CardDescription>
            Describe your IT issue or request. Our AI agent will classify and route it automatically.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="rounded-md bg-destructive/10 p-4 text-sm text-destructive">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                placeholder="Brief summary of your request"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                disabled={loading}
              />
              <p className="text-xs text-muted-foreground">
                Example: "Need VPN access for remote work" or "Laptop screen is cracked"
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="Provide detailed information about your request..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
                disabled={loading}
                rows={8}
              />
              <p className="text-xs text-muted-foreground">
                Include as much detail as possible to help us understand and resolve your request quickly.
              </p>
            </div>

            <div className="rounded-md bg-blue-50 p-4 text-sm text-blue-900">
              <p className="font-medium mb-1">What happens next?</p>
              <ul className="list-disc list-inside space-y-1 text-blue-800">
                <li>Your request will be automatically classified by our AI agent</li>
                <li>It will be assigned a severity level and routed to the appropriate team</li>
                <li>You'll receive updates as the request progresses</li>
                <li>You can chat with the agent for status updates or additional help</li>
              </ul>
            </div>

            <div className="flex gap-4">
              <Button type="submit" disabled={loading} className="flex-1">
                {loading ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                    Submitting...
                  </>
                ) : (
                  'Submit Request'
                )}
              </Button>
              <Link href="/requests">
                <Button type="button" variant="outline" disabled={loading}>
                  Cancel
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
