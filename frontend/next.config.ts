import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',

  // Experimental features for Next.js 15
  experimental: {
    
  },

  // TypeScript strict mode
  typescript: {
    ignoreBuildErrors: true,
  },

  // ESLint
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Image domains
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'api.gharmind.in' },
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: 'images.pexels.com' },
      { protocol: 'https', hostname: 'i.pravatar.cc' },
      { protocol: 'https', hostname: 'picsum.photos' },
    ],
  },

  // Environment variables (exposed to client)
  env: {
    NEXT_PUBLIC_APP_VERSION: process.env.npm_package_version ?? '1.0.0',
  },

  // Rewrites for API proxying in development
  async rewrites() {
    return process.env.NODE_ENV === 'development'
      ? [
          {
            source: '/api/:path*',
            destination: `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/v1'}/:path*`,
          },
        ]
      : []
  },
}

export default nextConfig
