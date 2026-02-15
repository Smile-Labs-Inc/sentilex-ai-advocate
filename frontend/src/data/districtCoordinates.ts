// =============================================================================
// District Coordinates for Sri Lanka
// Geographic coordinates for major districts in Sri Lanka
// =============================================================================

export interface DistrictCoordinates {
  latitude: number;
  longitude: number;
  name: string;
}

export const DISTRICT_COORDINATES: Record<string, DistrictCoordinates> = {
  Colombo: { latitude: 6.9271, longitude: 79.8612, name: "Colombo" },
  Gampaha: { latitude: 7.0910, longitude: 80.0150, name: "Gampaha" },
  Kalutara: { latitude: 6.5854, longitude: 79.9607, name: "Kalutara" },
  Kandy: { latitude: 7.2906, longitude: 80.6337, name: "Kandy" },
  Matale: { latitude: 7.4675, longitude: 80.6234, name: "Matale" },
  "Nuwara Eliya": { latitude: 6.9497, longitude: 80.7891, name: "Nuwara Eliya" },
  Galle: { latitude: 6.0535, longitude: 80.2210, name: "Galle" },
  Matara: { latitude: 5.9549, longitude: 80.5550, name: "Matara" },
  Hambantota: { latitude: 6.1429, longitude: 81.1212, name: "Hambantota" },
  Jaffna: { latitude: 9.6615, longitude: 80.0255, name: "Jaffna" },
  Kilinochchi: { latitude: 9.3961, longitude: 80.3988, name: "Kilinochchi" },
  Mannar: { latitude: 8.9810, longitude: 79.9044, name: "Mannar" },
  Vavuniya: { latitude: 8.7542, longitude: 80.4982, name: "Vavuniya" },
  Mullaitivu: { latitude: 9.2671, longitude: 80.8142, name: "Mullaitivu" },
  Batticaloa: { latitude: 7.7310, longitude: 81.6747, name: "Batticaloa" },
  Ampara: { latitude: 7.2978, longitude: 81.6747, name: "Ampara" },
  Trincomalee: { latitude: 8.5874, longitude: 81.2152, name: "Trincomalee" },
  Kurunegala: { latitude: 7.4863, longitude: 80.3623, name: "Kurunegala" },
  Puttalam: { latitude: 8.0362, longitude: 79.8283, name: "Puttalam" },
  Anuradhapura: { latitude: 8.3114, longitude: 80.4037, name: "Anuradhapura" },
  Polonnaruwa: { latitude: 7.9403, longitude: 81.0188, name: "Polonnaruwa" },
  Badulla: { latitude: 6.9934, longitude: 81.0550, name: "Badulla" },
  Moneragala: { latitude: 6.8728, longitude: 81.3507, name: "Moneragala" },
  Ratnapura: { latitude: 6.7056, longitude: 80.3847, name: "Ratnapura" },
  Kegalle: { latitude: 7.2513, longitude: 80.3464, name: "Kegalle" },
  Kalmunai: { latitude: 7.4088, longitude: 81.8358, name: "Kalmunai" },
};

// Sri Lanka center coordinates (used as default map center)
export const SRI_LANKA_CENTER: DistrictCoordinates = {
  latitude: 7.8731,
  longitude: 80.7718,
  name: "Sri Lanka",
};
