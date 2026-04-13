/** @type {import('next').NextConfig} */
const nextConfig = {
    rewrites: async () => {
        return [
            {
                source: '/api/pulse',
                destination: '/api/index.py',
            },
        ]
    },
}

export default nextConfig
