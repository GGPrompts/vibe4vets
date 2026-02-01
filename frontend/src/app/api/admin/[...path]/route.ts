/**
 * Admin API proxy route.
 *
 * This route proxies admin requests to the backend with the admin API key
 * stored securely on the server side. The key is never exposed to the browser.
 *
 * All requests to /api/admin/* are forwarded to the backend's /api/v1/admin/*
 * (and also /api/v1/feedback/admin/* and /api/v1/analytics/admin/*).
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const ADMIN_API_KEY = process.env.ADMIN_API_KEY;

// Map frontend admin paths to backend paths
function getBackendPath(path: string[]): string {
  const pathStr = path.join('/');

  // Handle feedback admin endpoints
  if (pathStr.startsWith('feedback/')) {
    return `/api/v1/feedback/admin/${pathStr.slice(9)}`;
  }
  if (pathStr === 'feedback') {
    return '/api/v1/feedback/admin';
  }

  // Handle analytics admin endpoints
  if (pathStr.startsWith('analytics/')) {
    return `/api/v1/analytics/admin/${pathStr.slice(10)}`;
  }
  if (pathStr === 'analytics') {
    return '/api/v1/analytics/admin';
  }

  // Default: forward to /api/v1/admin/*
  return `/api/v1/admin/${pathStr}`;
}

async function proxyRequest(
  request: NextRequest,
  path: string[],
  method: string
): Promise<NextResponse> {
  if (!ADMIN_API_KEY) {
    console.error('ADMIN_API_KEY is not configured');
    return NextResponse.json(
      { detail: 'Admin API not configured' },
      { status: 500 }
    );
  }

  const backendPath = getBackendPath(path);
  const url = new URL(backendPath, BACKEND_URL);

  // Forward query parameters
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.set(key, value);
  });

  const headers: HeadersInit = {
    'X-Admin-Key': ADMIN_API_KEY,
  };

  // Forward content-type for requests with body
  const contentType = request.headers.get('content-type');
  if (contentType) {
    headers['Content-Type'] = contentType;
  }

  try {
    const fetchOptions: RequestInit = {
      method,
      headers,
    };

    // Forward body for POST, PATCH, PUT, DELETE
    if (['POST', 'PATCH', 'PUT', 'DELETE'].includes(method)) {
      const body = await request.text();
      if (body) {
        fetchOptions.body = body;
      }
    }

    const response = await fetch(url.toString(), fetchOptions);

    // Forward the response
    const data = await response.json().catch(() => null);

    return NextResponse.json(data ?? { detail: 'No response body' }, {
      status: response.status,
    });
  } catch (error) {
    console.error('Admin proxy error:', error);
    const message = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { detail: `Backend connection failed: ${message}` },
      { status: 502 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'POST');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'PATCH');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'DELETE');
}
