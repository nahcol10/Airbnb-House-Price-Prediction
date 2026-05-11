'use client';

import { useState } from 'react';
import {
  Home,
  Star,
  MapPin,
  Settings2,
  DollarSign,
  Loader2,
  BedDouble,
  Wifi,
  Shield,
  Zap,
  Sparkles,
} from 'lucide-react';
import type { PredictionRequest } from '@/types';

interface PredictionFormProps {
  onPredict: (data: PredictionRequest) => void;
  loading: boolean;
}

const CITIES = ['NYC', 'LA', 'SF', 'Chicago', 'DC', 'Boston'] as const;
const ROOM_TYPES = ['Entire home/apt', 'Private room', 'Shared room'] as const;
const PROPERTY_TYPES = [
  'Apartment',
  'House',
  'Condominium',
  'Loft',
  'Townhouse',
  'Guest suite',
  'Villa',
  'Other',
] as const;
const BED_TYPES = [
  'Real Bed',
  'Futon',
  'Pull-out Sofa',
  'Couch',
  'Airbed',
] as const;
const CANCELLATION_POLICIES = [
  'flexible',
  'moderate',
  'strict',
  'super_strict_30',
  'super_strict_60',
] as const;

export default function PredictionForm({
  onPredict,
  loading,
}: PredictionFormProps) {
  const [formData, setFormData] = useState<PredictionRequest>({
    accommodates: 2,
    bathrooms: 1,
    bedrooms: 1,
    beds: 1,
    city: 'NYC',
    room_type: 'Entire home/apt',
    property_type: 'Apartment',
    cleaning_fee: true,
    host_has_profile_pic: true,
    host_identity_verified: true,
    host_response_rate: 90,
    instant_bookable: true,
    number_of_reviews: 10,
    review_scores_rating: 95,
    latitude: 40.75,
    longitude: -73.98,
    zipcode: '',
    neighbourhood: '',
    bed_type: 'Real Bed',
    cancellation_policy: 'flexible',
    amenity_count: 15,
  });

  const handleChange = (
    field: keyof PredictionRequest,
    value: string | number | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onPredict(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* ── Property Details ── */}
      <div className="section-card animate-fade-in">
        <h2 className="section-title">
          <Home className="w-5 h-5 text-airbnb-pink" />
          Property Details
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* City */}
          <div>
            <label htmlFor="city" className="form-label">
              City
            </label>
            <select
              id="city"
              value={formData.city}
              onChange={(e) => handleChange('city', e.target.value)}
              className="form-select"
            >
              {CITIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* Room Type */}
          <div>
            <label htmlFor="room_type" className="form-label">
              Room Type
            </label>
            <select
              id="room_type"
              value={formData.room_type}
              onChange={(e) => handleChange('room_type', e.target.value)}
              className="form-select"
            >
              {ROOM_TYPES.map((rt) => (
                <option key={rt} value={rt}>
                  {rt}
                </option>
              ))}
            </select>
          </div>

          {/* Property Type */}
          <div>
            <label htmlFor="property_type" className="form-label">
              Property Type
            </label>
            <select
              id="property_type"
              value={formData.property_type}
              onChange={(e) => handleChange('property_type', e.target.value)}
              className="form-select"
            >
              {PROPERTY_TYPES.map((pt) => (
                <option key={pt} value={pt}>
                  {pt}
                </option>
              ))}
            </select>
          </div>

          {/* Accommodates */}
          <div>
            <label htmlFor="accommodates" className="form-label">
              Accommodates
            </label>
            <input
              id="accommodates"
              type="number"
              min={1}
              max={16}
              value={formData.accommodates}
              onChange={(e) =>
                handleChange('accommodates', parseInt(e.target.value) || 1)
              }
              className="form-input"
            />
          </div>

          {/* Bedrooms */}
          <div>
            <label htmlFor="bedrooms" className="form-label">
              Bedrooms
            </label>
            <input
              id="bedrooms"
              type="number"
              min={0}
              max={10}
              value={formData.bedrooms}
              onChange={(e) =>
                handleChange('bedrooms', parseInt(e.target.value) || 0)
              }
              className="form-input"
            />
          </div>

          {/* Beds */}
          <div>
            <label htmlFor="beds" className="form-label">
              Beds
            </label>
            <input
              id="beds"
              type="number"
              min={0}
              max={10}
              value={formData.beds}
              onChange={(e) =>
                handleChange('beds', parseInt(e.target.value) || 0)
              }
              className="form-input"
            />
          </div>

          {/* Bathrooms */}
          <div>
            <label htmlFor="bathrooms" className="form-label">
              Bathrooms
            </label>
            <input
              id="bathrooms"
              type="number"
              min={0}
              max={8}
              step={0.5}
              value={formData.bathrooms}
              onChange={(e) =>
                handleChange('bathrooms', parseFloat(e.target.value) || 0)
              }
              className="form-input"
            />
          </div>
        </div>
      </div>

      {/* ── Host & Reviews ── */}
      <div className="section-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <h2 className="section-title">
          <Star className="w-5 h-5 text-airbnb-pink" />
          Host & Reviews
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label htmlFor="host_response_rate" className="form-label">
              Host Response Rate (%)
            </label>
            <input
              id="host_response_rate"
              type="number"
              min={0}
              max={100}
              value={formData.host_response_rate}
              onChange={(e) =>
                handleChange(
                  'host_response_rate',
                  parseInt(e.target.value) || 0
                )
              }
              className="form-input"
            />
          </div>
          <div>
            <label htmlFor="number_of_reviews" className="form-label">
              Number of Reviews
            </label>
            <input
              id="number_of_reviews"
              type="number"
              min={0}
              max={1000}
              value={formData.number_of_reviews}
              onChange={(e) =>
                handleChange(
                  'number_of_reviews',
                  parseInt(e.target.value) || 0
                )
              }
              className="form-input"
            />
          </div>
          <div>
            <label htmlFor="review_scores_rating" className="form-label">
              Review Score Rating
            </label>
            <input
              id="review_scores_rating"
              type="number"
              min={0}
              max={100}
              value={formData.review_scores_rating}
              onChange={(e) =>
                handleChange(
                  'review_scores_rating',
                  parseInt(e.target.value) || 0
                )
              }
              className="form-input"
            />
          </div>
        </div>
      </div>

      {/* ── Features ── */}
      <div className="section-card animate-fade-in" style={{ animationDelay: '0.15s' }}>
        <h2 className="section-title">
          <Settings2 className="w-5 h-5 text-airbnb-pink" />
          Features
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label className="flex items-center gap-3 cursor-pointer group p-3 rounded-xl hover:bg-gray-50 transition-colors duration-200">
            <input
              type="checkbox"
              checked={formData.cleaning_fee}
              onChange={(e) =>
                handleChange('cleaning_fee', e.target.checked)
              }
              className="form-checkbox"
            />
            <div>
              <span className="text-sm font-medium text-gray-800 group-hover:text-airbnb-pink transition-colors">
                Cleaning Fee
              </span>
              <p className="text-xs text-gray-500">Charges a separate cleaning fee</p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer group p-3 rounded-xl hover:bg-gray-50 transition-colors duration-200">
            <input
              type="checkbox"
              checked={formData.host_has_profile_pic}
              onChange={(e) =>
                handleChange('host_has_profile_pic', e.target.checked)
              }
              className="form-checkbox"
            />
            <div>
              <span className="text-sm font-medium text-gray-800 group-hover:text-airbnb-pink transition-colors">
                Host Has Profile Pic
              </span>
              <p className="text-xs text-gray-500">Host has a verified photo</p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer group p-3 rounded-xl hover:bg-gray-50 transition-colors duration-200">
            <input
              type="checkbox"
              checked={formData.host_identity_verified}
              onChange={(e) =>
                handleChange('host_identity_verified', e.target.checked)
              }
              className="form-checkbox"
            />
            <div>
              <span className="text-sm font-medium text-gray-800 group-hover:text-airbnb-pink transition-colors">
                <Shield className="w-3.5 h-3.5 inline mr-1" />
                Host Identity Verified
              </span>
              <p className="text-xs text-gray-500">Host&apos;s identity has been verified</p>
            </div>
          </label>

          <label className="flex items-center gap-3 cursor-pointer group p-3 rounded-xl hover:bg-gray-50 transition-colors duration-200">
            <input
              type="checkbox"
              checked={formData.instant_bookable}
              onChange={(e) =>
                handleChange('instant_bookable', e.target.checked)
              }
              className="form-checkbox"
            />
            <div>
              <span className="text-sm font-medium text-gray-800 group-hover:text-airbnb-pink transition-colors">
                <Zap className="w-3.5 h-3.5 inline mr-1" />
                Instant Bookable
              </span>
              <p className="text-xs text-gray-500">Book instantly without host approval</p>
            </div>
          </label>
        </div>
      </div>

      {/* ── Location ── */}
      <div className="section-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <h2 className="section-title">
          <MapPin className="w-5 h-5 text-airbnb-pink" />
          Location & Details
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label htmlFor="latitude" className="form-label">
              Latitude
            </label>
            <input
              id="latitude"
              type="number"
              step="0.0001"
              value={formData.latitude}
              onChange={(e) =>
                handleChange('latitude', parseFloat(e.target.value) || 0)
              }
              className="form-input"
            />
          </div>
          <div>
            <label htmlFor="longitude" className="form-label">
              Longitude
            </label>
            <input
              id="longitude"
              type="number"
              step="0.0001"
              value={formData.longitude}
              onChange={(e) =>
                handleChange('longitude', parseFloat(e.target.value) || 0)
              }
              className="form-input"
            />
          </div>
          <div>
            <label htmlFor="zipcode" className="form-label">
              Zipcode
            </label>
            <input
              id="zipcode"
              type="text"
              placeholder="e.g. 10001"
              value={formData.zipcode}
              onChange={(e) => handleChange('zipcode', e.target.value)}
              className="form-input"
            />
          </div>
          <div>
            <label htmlFor="bed_type" className="form-label">
              <BedDouble className="w-3.5 h-3.5 inline mr-1" />
              Bed Type
            </label>
            <select
              id="bed_type"
              value={formData.bed_type}
              onChange={(e) => handleChange('bed_type', e.target.value)}
              className="form-select"
            >
              {BED_TYPES.map((bt) => (
                <option key={bt} value={bt}>
                  {bt}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="cancellation_policy" className="form-label">
              Cancellation Policy
            </label>
            <select
              id="cancellation_policy"
              value={formData.cancellation_policy}
              onChange={(e) =>
                handleChange('cancellation_policy', e.target.value)
              }
              className="form-select"
            >
              {CANCELLATION_POLICIES.map((cp) => (
                <option key={cp} value={cp}>
                  {cp.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* ── Amenities ── */}
      <div className="section-card animate-fade-in" style={{ animationDelay: '0.25s' }}>
        <h2 className="section-title">
          <Wifi className="w-5 h-5 text-airbnb-pink" />
          Amenities
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label htmlFor="amenity_count" className="form-label">
              <Sparkles className="w-3.5 h-3.5 inline mr-1" />
              Amenity Count
            </label>
            <input
              id="amenity_count"
              type="number"
              min={0}
              max={50}
              value={formData.amenity_count}
              onChange={(e) =>
                handleChange('amenity_count', parseInt(e.target.value) || 0)
              }
              className="form-input"
            />
            <p className="text-xs text-gray-400 mt-1">
              Total number of amenities offered
            </p>
          </div>
        </div>
      </div>

      {/* ── Submit Button ── */}
      <div className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
        <button
          type="submit"
          disabled={loading}
          className="btn-predict flex items-center justify-center gap-3"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Predicting...
            </>
          ) : (
            <>
              <DollarSign className="w-5 h-5" />
              Predict Price
            </>
          )}
        </button>
      </div>
    </form>
  );
}
