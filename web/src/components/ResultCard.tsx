'use client';

import { CircleCheckBig, TrendingUp, Calculator } from 'lucide-react';
import type { PredictionResponse } from '@/types';

interface ResultCardProps {
  prediction: PredictionResponse;
}

export default function ResultCard({ prediction }: ResultCardProps) {
  const { log_price, price_usd } = prediction;

  return (
    <div className="animate-scale-in">
      <div className="relative overflow-hidden rounded-airbnbXl bg-gradient-to-br from-white via-white to-airbnb-cream/50 border border-airbnb-pink/20 shadow-airbnbLg">
        {/* Decorative elements */}
        <div className="absolute -top-12 -right-12 w-32 h-32 bg-airbnb-pink/5 rounded-full blur-2xl" />
        <div className="absolute -bottom-8 -left-8 w-24 h-24 bg-airbnb-coral/5 rounded-full blur-xl" />

        <div className="relative p-8 sm:p-10">
          {/* Success indicator */}
          <div className="flex items-center gap-2 mb-6">
            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-emerald-100">
              <CircleCheckBig className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-emerald-700 uppercase tracking-wider">
                Prediction Complete
              </h3>
              <p className="text-xs text-gray-500">
                Based on XGBoost model analysis
              </p>
            </div>
          </div>

          {/* Main price */}
          <div className="text-center mb-8">
            <p className="text-sm font-medium text-gray-500 mb-2">
              Estimated Nightly Price
            </p>
            <div className="flex items-baseline justify-center gap-1">
              <span className="text-lg font-medium text-gray-400">$</span>
              <span className="text-6xl sm:text-7xl font-extrabold gradient-text leading-none">
                {price_usd.toFixed(0)}
              </span>
              <span className="text-lg font-medium text-gray-400">USD</span>
            </div>
            <p className="text-xs text-gray-400 mt-2">per night</p>
          </div>

          {/* Divider */}
          <div className="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent mb-8" />

          {/* Stats grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center p-4 rounded-airbnb bg-gray-50/80">
              <Calculator className="w-5 h-5 text-airbnb-pink mx-auto mb-2" />
              <p className="text-xs text-gray-500 font-medium">Log Price</p>
              <p className="text-lg font-bold text-gray-800 mt-1">
                {log_price.toFixed(4)}
              </p>
            </div>
            <div className="text-center p-4 rounded-airbnb bg-gray-50/80">
              <TrendingUp className="w-5 h-5 text-airbnb-pink mx-auto mb-2" />
              <p className="text-xs text-gray-500 font-medium">Monthly Estimate</p>
              <p className="text-lg font-bold text-gray-800 mt-1">
                ${(price_usd * 30).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
              </p>
            </div>
            <div className="text-center p-4 rounded-airbnb bg-gray-50/80">
              <CircleCheckBig className="w-5 h-5 text-emerald-500 mx-auto mb-2" />
              <p className="text-xs text-gray-500 font-medium">Model Confidence</p>
              <p className="text-lg font-bold text-gray-800 mt-1">High</p>
            </div>
          </div>

          {/* Disclaimer */}
          <p className="text-[11px] text-center text-gray-400 mt-6 leading-relaxed">
            This prediction is an estimate based on our machine learning model.
            Actual prices may vary based on seasonality, demand, and other market factors.
          </p>
        </div>
      </div>
    </div>
  );
}
