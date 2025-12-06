import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "WhyExplore - Discover Videos You'll Actually Want to Watch",
  description:
    "Break free from YouTube's repetitive algorithm. Explore videos through an interactive genre tree and AI-powered recommendations based on your taste.",
  generator: "v0.app",
  icons: {
    icon: "/vintage-camera.png",
    apple: "/vintage-camera.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
