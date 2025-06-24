import { withBaml } from '@boundaryml/baml-nextjs-plugin';
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true
  },
  typescript: {
    ignoreBuildErrors: false
  }
};

export default withBaml()(nextConfig);
