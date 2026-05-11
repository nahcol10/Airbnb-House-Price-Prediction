export interface PredictionRequest {
  accommodates: number;
  bathrooms: number;
  bedrooms: number;
  beds: number;
  city: string;
  room_type: string;
  property_type: string;
  cleaning_fee: boolean;
  host_has_profile_pic: boolean;
  host_identity_verified: boolean;
  host_response_rate: number;
  instant_bookable: boolean;
  number_of_reviews: number;
  review_scores_rating: number;
  latitude: number;
  longitude: number;
  zipcode: string;
  neighbourhood: string;
  bed_type: string;
  cancellation_policy: string;
  amenity_count: number;
}

export interface PredictionResponse {
  log_price: number;
  price_usd: number;
}
