// types/api.d.ts

export interface Coordinate {
  x: number
  y: number
}

export interface CoordinateWGS84 {
  latitude: number
  longitude: number
  utm_zone_detected: number
}

export interface Metadata {
  coordinate_count: number
  coordinate_system_utm: string
  coordinate_system_wgs84: string
  preprocessing_applied: boolean
  extraction_method: string
}

export interface ExtractResponse {
  id?: string // identifiant unique ajouté par le store
  filename: string
  timestamp: string
  extraction_success: boolean
  coordinates: string // JSON stringified array of Coordinate
  coordinates_wgs84: CoordinateWGS84[]

  aif: "OUI" | "NON"
  air_proteges: "OUI" | "NON"
  dpl: "OUI" | "NON"
  dpm: "OUI" | "NON"
  enregistrement_individuel: "OUI" | "NON"
  litige: "OUI" | "NON"
  parcelles: "OUI" | "NON"
  restriction: "OUI" | "NON"
  tf_demembres: "OUI" | "NON"
  tf_en_cours: "OUI" | "NON"
  tf_etat: "OUI" | "NON"
  titre_reconstitue: "OUI" | "NON"
  zone_inondable: "OUI" | "NON"

  metadata: Metadata
}
