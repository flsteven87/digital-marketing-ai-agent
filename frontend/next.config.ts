import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Disable image optimization for Docker (can be enabled with custom loader)
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
