/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  rewrites: async () => {
    return [
      {
        source: '/api/pulse',
        destination: '/api/index.py',
      },
    ]
  },
}

module.exports = nextConfig
