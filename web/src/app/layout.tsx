import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Airbnb Price Predictor',
  description:
    'Predict optimal pricing for your Airbnb listing using machine learning powered by XGBoost. Get accurate price estimates based on property details, location, amenities, and market trends.',
  keywords: [
    'airbnb',
    'price predictor',
    'machine learning',
    'xgboost',
    'rental pricing',
    'property valuation',
  ],
  authors: [{ name: 'Airbnb Price Predictor Team' }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
