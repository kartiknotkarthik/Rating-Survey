import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'GROWW Pulse | Review Analyzer',
  description: 'Automated weekly product feedback analysis for GROWW.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-[#0f172a] antialiased">{children}</body>
    </html>
  )
}
