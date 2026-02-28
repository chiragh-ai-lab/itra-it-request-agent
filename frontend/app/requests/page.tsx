'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { requestsApi } from '@/lib/api-client';
import { PlusCircle, Search } from 'lucide-react';
import { formatDate, getStatusColor, getSeverityColor } from '@/lib/utils';
import { Input } from '@/components/ui/input';

interface Request {
  request_id: string;
  title: string;
  description: string;
  status: string;
  severity?: number;
  category?: string;
  routing_team?: string;
  created_at: string;
  updated_at: string;
}

export default function RequestsPage() {
  const [requests, setRequests] = useState<Request[]>([]);
  const [filteredRequests, setFilteredRequests] = useState<Request[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  useEffect(() => {
    loadRequests();
  }, []);

  useEffect(() => {
    filterRequests();
  }, [requests, searchTerm, statusFilter, categoryFilter]);

  const loadRequests = async () => {
    try {
      const data = await requestsApi.list();
      setRequests(data.requests || []);
      setFilteredRequests(data.requests || []);
    } catch (error) {
      console.error('Error loading requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterRequests = () => {
    let filtered = [...requests];

    if (searchTerm) {
      filtered = filtered.filter(
        (r) =>
          r.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          r.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((r) => r.status === statusFilter);
    }

    if (categoryFilter !== 'all') {
      filtered = filtered.filter((r) => r.category === categoryFilter);
    }

    setFilteredRequests(filtered);
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading requests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Requests</h1>
          <p className="text-muted-foreground mt-2">Manage your IT requests</p>
        </div>
        <Link href="/requests/new">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Request
          </Button>
        </Link>
      </div>

      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search requests..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="all">All Statuses</option>
              <option value="submitted">Submitted</option>
              <option value="classified">Classified</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>

            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="all">All Categories</option>
              <option value="access">Access</option>
              <option value="hardware">Hardware</option>
              <option value="software">Software</option>
              <option value="cloud">Cloud</option>
              <option value="network">Network</option>
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            {filteredRequests.length} {filteredRequests.length === 1 ? 'Request' : 'Requests'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredRequests.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>No requests found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredRequests.map((request) => (
                <Link
                  key={request.request_id}
                  href={`/requests/${request.request_id}`}
                  className="block p-4 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium truncate">{request.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {request.description}
                      </p>
                      <div className="flex flex-wrap items-center gap-2 mt-3">
                        <span className="text-xs text-muted-foreground">
                          {formatDate(request.created_at)}
                        </span>
                        {request.category && (
                          <Badge variant="outline" className="capitalize">
                            {request.category}
                          </Badge>
                        )}
                        {request.severity && (
                          <Badge className={getSeverityColor(request.severity)}>
                            Severity {request.severity}
                          </Badge>
                        )}
                        {request.routing_team && (
                          <Badge variant="secondary" className="capitalize">
                            {request.routing_team}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <Badge className={getStatusColor(request.status)}>
                      {request.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
