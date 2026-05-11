'use client';

import { useState } from 'react';
import { Home as HomeIcon, TrendingUp, Code2, Database, Zap } from 'lucide-react';
import PredictionForm from '@/components/PredictionForm';
import ResultCard from '@/components/ResultCard';
import { predictPrice } from '@/lib/api';
import type { PredictionResponse } from '@/types';

export default function Home() {
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async (data: Parameters<typeof predictPrice>[0]) => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await predictPrice(data);
      setPrediction(result);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'An unexpected error occurred. Please make sure the backend server is running.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Header ── */}
      <header className="sticky top-0 z-50 glass-effect bg-white/80 border-b border-gray-100">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-18">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-airbnb bg-airbnb-pink text-white shadow-airbnbPink">
                <HomeIcon className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-gray-900 leading-tight">
                  Airbnb Price Predictor
                </h1>
                <p className="text-xs text-gray-500 hidden sm:block">
                  ML-powered pricing estimates
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Zap className="w-3.5 h-3.5 text-airbnb-pink" />
              <span className="hidden sm:inline">XGBoost Model</span>
            </div>
          </div>
        </div>
      </header>

      {/* ── Hero Section ── */}
      <section className="relative overflow-hidden bg-gradient-to-b from-airbnb-cream/60 via-white to-white">
        {/* Background decorative circles */}
        <div className="absolute top-0 left-1/4 w-64 h-64 bg-airbnb-pink/3 rounded-full blur-3xl" />
        <div className="absolute top-10 right-1/4 w-48 h-48 bg-airbnb-coral/3 rounded-full blur-3xl" />

        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-airbnb-pink/10 text-airbnb-pink text-xs font-semibold mb-4">
            <TrendingUp className="w-3.5 h-3.5" />
            Machine Learning Powered
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-gray-900 mb-4 text-balance">
            Predict Your Airbnb{' '}
            <span className="gradient-text">Optimal Price</span>
          </h2>
          <p className="text-base sm:text-lg text-gray-500 max-w-2xl mx-auto leading-relaxed">
            Enter your property details and get an instant, data-driven price estimate
            powered by our XGBoost machine learning model trained on millions of listings.
          </p>
        </div>
      </section>

      {/* ── Main Content ── */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 rounded-airbnb bg-red-50 border border-red-200 animate-slide-up">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-5 h-5 mt-0.5 rounded-full bg-red-100 flex items-center justify-center">
                <span className="text-red-500 text-xs font-bold">!</span>
              </div>
              <div>
                <p className="text-sm font-semibold text-red-800">
                  Prediction Failed
                </p>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Form */}
        <div className="max-w-3xl mx-auto">
          <PredictionForm onPredict={handlePredict} loading={loading} />
        </div>

        {/* Prediction Result */}
        {prediction && (
          <div className="mt-8 mb-8 animate-slide-up">
            <ResultCard prediction={prediction} />
          </div>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="mt-auto border-t border-gray-100 bg-white/60 glass-effect">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-airbnb-pink/10">
                <HomeIcon className="w-4 h-4 text-airbnb-pink" />
              </div>
              <p className="text-sm text-gray-500">
                Built with{' '}
                <span className="inline-flex items-center gap-1 font-semibold text-gray-700">
                  <Database className="w-3.5 h-3.5 text-airbnb-pink" />
                  XGBoost
                </span>
                {' · '}
                <span className="inline-flex items-center gap-1 font-semibold text-gray-700">
                  <Code2 className="w-3.5 h-3.5 text-airbnb-pink" />
                  React
                </span>
                {' · '}
                <span className="inline-flex items-center gap-1 font-semibold text-gray-700">
                  <Zap className="w-3.5 h-3.5 text-airbnb-pink" />
                  FastAPI
                </span>
              </p>
            </div>
            <p className="text-xs text-gray-400">
              © {new Date().getFullYear()} Airbnb Price Predictor
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
