import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthWrapper } from "@/components/auth-wrapper";
import { Sidebar } from "@/components/sidebar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "IT Request Agent",
  description: "AI-powered IT request management system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.variable}>
        <AuthWrapper>
          <div className="flex h-screen">
            <Sidebar />
            <main className="flex-1 overflow-y-auto bg-gray-50">
              {children}
            </main>
          </div>
        </AuthWrapper>
      </body>
    </html>
  );
}
