'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { requestsApi } from '@/lib/api-client';
import { ArrowLeft, MessageSquare, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { formatDate, getStatusColor, getSeverityColor } from '@/lib/utils';

interface Request {
  request_id: string;
  title: string;
  description: string;
  status: string;
  severity?: number;
  category?: string;
  routing_team?: string;
  classification_confidence?: number;
  submitter_email: string;
  submitter_name: string;
  agent_actions: any[];
  resolution?: any;
  created_at: string;
  updated_at: string;
}

export default function RequestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [request, setRequest] = useState<Request | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatMessage, setChatMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatResponse, setChatResponse] = useState('');
  const [resolveText, setResolveText] = useState('');
  const [resolveLoading, setResolveLoading] = useState(false);
  const [classifying, setClassifying] = useState(false);

  useEffect(() => {
    loadRequest();
  }, [params.id]);

  const loadRequest = async () => {
    try {
      const data = await requestsApi.get(params.id as string);
      setRequest(data.request);
    } catch (error) {
      console.error('Error loading request:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    setChatLoading(true);
    try {
      const response = await requestsApi.chat(params.id as string, chatMessage);
      setChatResponse(response.message);
      setChatMessage('');
    } catch (error) {
      console.error('Error chatting:', error);
    } finally {
      setChatLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!resolveText.trim()) return;

    setResolveLoading(true);
    try {
      await requestsApi.resolve(params.id as string, resolveText);
      loadRequest();
      setResolveText('');
    } catch (error) {
      console.error('Error resolving:', error);
    } finally {
      setResolveLoading(false);
    }
  };

  const handleClassify = async () => {
    alert('🔵 Button clicked! Check console for details.');
    console.log('🔵 Classification button clicked');
    console.log('🔵 Request ID:', params.id);
    console.log('🔵 Request object:', request);
    setClassifying(true);
    
    try {
      console.log('🔵 Calling classify API...');
      const result = await requestsApi.classify(params.id as string);
      console.log('🔵 Classify API response:', result);
      
      // Poll for classification completion
      let attempts = 0;
      const maxAttempts = 15; // 30 seconds max
      console.log('🔵 Starting polling for classification completion...');
      
      const pollInterval = setInterval(async () => {
        attempts++;
        console.log(`🔵 Poll attempt ${attempts}/${maxAttempts}`);
        
        try {
          const data = await requestsApi.get(params.id as string);
          console.log('🔵 Current request status:', data.request.status);
          
          if (data.request.status !== 'submitted' || attempts >= maxAttempts) {
            clearInterval(pollInterval);
            console.log('🔵 Classification complete or timeout reached');
            setRequest(data.request);
            setClassifying(false);
            
            if (data.request.status === 'classified') {
              alert('✅ Classification complete! Check the Details section for results.');
            } else if (attempts >= maxAttempts) {
              alert('⏱️ Classification is taking longer than expected. Please refresh the page.');
            }
          }
        } catch (pollError) {
          console.error('🔴 Error during polling:', pollError);
        }
      }, 2000);
    } catch (error) {
      console.error('🔴 Error classifying:', error);
      alert(`❌ Classification failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setClassifying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading request...</p>
        </div>
      </div>
    );
  }

  if (!request) {
    return (
      <div className="p-8">
        <div className="text-center">
          <p className="text-muted-foreground">Request not found</p>
          <Link href="/requests">
            <Button className="mt-4">Back to Requests</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <Link
        href="/requests"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to requests
      </Link>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-2xl">{request.title}</CardTitle>
                  <CardDescription className="mt-2">
                    Submitted by {request.submitter_name} on {formatDate(request.created_at)}
                  </CardDescription>
                </div>
                <Badge className={getStatusColor(request.status)}>
                  {request.status.replace('_', ' ')}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">Description</h3>
                <p className="text-muted-foreground whitespace-pre-wrap">{request.description}</p>
              </div>

              {request.resolution && (
                <div className="rounded-md bg-green-50 p-4">
                  <h3 className="font-medium text-green-900 mb-2">Resolution</h3>
                  <p className="text-green-800">{request.resolution.resolution_text}</p>
                  <p className="text-xs text-green-700 mt-2">
                    Resolved by {request.resolution.resolved_by} on {formatDate(request.resolution.resolved_at)}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="rounded-full bg-blue-100 p-2">
                      <Clock className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="w-px flex-1 bg-border mt-2"></div>
                  </div>
                  <div className="flex-1 pb-4">
                    <p className="font-medium">Request Submitted</p>
                    <p className="text-sm text-muted-foreground">{formatDate(request.created_at)}</p>
                  </div>
                </div>

                {request.agent_actions && request.agent_actions.length > 0 && request.agent_actions.map((action, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`rounded-full p-2 ${action.status === 'blocked' ? 'bg-red-100' : 'bg-purple-100'}`}>
                        <AlertCircle className={`h-4 w-4 ${action.status === 'blocked' ? 'text-red-600' : 'text-purple-600'}`} />
                      </div>
                      {index < request.agent_actions.length - 1 && (
                        <div className="w-px flex-1 bg-border mt-2"></div>
                      )}
                    </div>
                    <div className="flex-1 pb-4">
                      <p className="font-medium capitalize">{action.action.replace('_', ' ')}</p>
                      <p className="text-sm text-muted-foreground">{formatDate(action.timestamp)}</p>
                      {action.result && (
                        <p className="text-sm mt-1">{action.result.message || JSON.stringify(action.result)}</p>
                      )}
                      {action.status === 'blocked' && (
                        <p className="text-sm text-red-600 mt-1">Blocked: {action.reason}</p>
                      )}
                    </div>
                  </div>
                ))}

                {request.status === 'resolved' && request.resolution && (
                  <div className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="rounded-full bg-green-100 p-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">Request Resolved</p>
                      <p className="text-sm text-muted-foreground">{formatDate(request.resolution.resolved_at)}</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MessageSquare className="mr-2 h-5 w-5" />
                Chat with Agent
              </CardTitle>
              <CardDescription>Ask questions about your request</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {chatResponse && (
                <div className="rounded-md bg-blue-50 p-4">
                  <p className="text-sm text-blue-900">{chatResponse}</p>
                </div>
              )}
              
              <form onSubmit={handleChat} className="space-y-4">
                <Textarea
                  placeholder="Type your message..."
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  disabled={chatLoading}
                  rows={3}
                />
                <Button type="submit" disabled={chatLoading}>
                  {chatLoading ? 'Sending...' : 'Send Message'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Request ID</p>
                <p className="text-sm font-mono">{request.request_id}</p>
              </div>

              {request.category && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Category</p>
                  <Badge variant="outline" className="capitalize mt-1">
                    {request.category}
                  </Badge>
                </div>
              )}

              {request.severity && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Severity</p>
                  <Badge className={`${getSeverityColor(request.severity)} mt-1`}>
                    Level {request.severity}
                  </Badge>
                </div>
              )}

              {request.routing_team && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Routing Team</p>
                  <Badge variant="secondary" className="capitalize mt-1">
                    {request.routing_team}
                  </Badge>
                </div>
              )}

              {request.classification_confidence && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Classification Confidence</p>
                  <p className="text-sm">{(request.classification_confidence * 100).toFixed(0)}%</p>
                </div>
              )}

              <div>
                <p className="text-sm font-medium text-muted-foreground">Last Updated</p>
                <p className="text-sm">{formatDate(request.updated_at)}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {request.status === 'submitted' && (
                <>
                  <Button 
                    onClick={() => alert('Test button works!')} 
                    variant="secondary" 
                    className="w-full"
                  >
                    Test Button (Click Me First)
                  </Button>
                  <Button 
                    onClick={handleClassify} 
                    variant="outline" 
                    className="w-full"
                    disabled={classifying}
                  >
                    {classifying ? 'Classifying...' : 'Trigger Classification'}
                  </Button>
                </>
              )}
              
              {classifying && (
                <p className="text-xs text-muted-foreground text-center">
                  AI is analyzing your request...
                </p>
              )}

              {request.status !== 'resolved' && (
                <div className="space-y-2">
                  <Textarea
                    placeholder="Resolution details..."
                    value={resolveText}
                    onChange={(e) => setResolveText(e.target.value)}
                    rows={3}
                  />
                  <Button
                    onClick={handleResolve}
                    disabled={resolveLoading || !resolveText.trim()}
                    className="w-full"
                  >
                    {resolveLoading ? 'Resolving...' : 'Mark as Resolved'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
