<template>
  <div ref="mapContainer" class="map-container"></div>
  <div class="map-controls">
    <button class="zoom-button" @click="zoomIn" title="Zoom avant">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
    </button>
    <button class="zoom-button" @click="zoomOut" title="Zoom arrière">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
    </button>
    <button class="recenter-button" @click="recenterMap" title="Recentrer sur le Bénin">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
      </svg>
    </button>
    <button id="zoom-parcel-btn" class="recenter-button" @click="() => { console.log('[DOM] bouton oeil cliqué'); fitToParcel(); }" title="Zoomer sur la parcelle">
      <!-- Icône d'œil Lucide (i-lucide-eye) -->
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
// Flag global pour ne zoomer qu'une seule fois par navigation
if (typeof window !== 'undefined' && window.__carteZoomed === undefined) {
  window.__carteZoomed = false;
}
// --- Déclarer fitToParcel en haut pour garantir le scope ---
const fitToParcel = () => {
  console.log('[fitToParcel] called');
  if (!map.value || !props.parcelCoords || props.parcelCoords.length < 3) return;
  const coords = props.parcelCoords;
  const closedCoords = coords[0] !== coords[coords.length - 1] ? [...coords, coords[0]] : coords;
  const bounds = closedCoords.reduce(
    (b, coord) => b.extend(coord),
    new maplibregl.LngLatBounds(closedCoords[0], closedCoords[0])
  );
  map.value.fitBounds(bounds, { padding: 40 });
  console.log('[fitToParcel] fitBounds called');
};
import { ref, onMounted, watch } from 'vue';
import maplibregl from 'maplibre-gl';

const emit = defineEmits(['update:loading']);

const props = defineProps({
  visibleLayers: {
    type: Array,
    required: true,
  },
  parcelCoords: {
    type: Array,
  },
  shouldDrawParcel: {
    type: Boolean,
    default: false,
  },
  couchesDisponibles: {
    type: Array,
    default: () => []
  }
});

const mapContainer = ref(null);
const map = ref(null);
const center = [2.3158, 9.3077]; // Coordonnées du Bénin [lng, lat]
const zoom = 6;

const recenterMap = () => {
  if (map.value) {
    map.value.flyTo({
      center: center,
      zoom: zoom,
      essential: true,
      duration: 1000
    });
  }
};

const zoomIn = () => {
  if (map.value) {
    const currentZoom = map.value.getZoom();
    map.value.zoomTo(currentZoom + 1, {
      duration: 300
    });
  }
};

const zoomOut = () => {
  if (map.value) {
    const currentZoom = map.value.getZoom();
    map.value.zoomTo(currentZoom - 1, {
      duration: 300
    });
  }
};

const allLayerIds = [
  'aif',
  'air_proteges',
  'dpl',
  'dpm',
  'enregistrement individuel',
  'litige',
  'restriction',
  'tf_demembres',
  'tf_en_cours',
  'tf_etat',
  'titre_reconstitue',
  'zone_inondable',
  'parcelles'
];

const updateLayerVisibility = () => {
  if (!map.value || !map.value.isStyleLoaded()) return;

  allLayerIds.forEach(id => {
    const isVisible = props.visibleLayers.includes(id);
    if (map.value.getLayer(`${id}-fill`)) {
      map.value.setLayoutProperty(`${id}-fill`, 'visibility', isVisible ? 'visible' : 'none');
      map.value.setLayoutProperty(`${id}-line`, 'visibility', isVisible ? 'visible' : 'none');
    }
  });
};

onMounted(() => {
  // Zoom sur la parcelle uniquement la toute première fois (pas lors d'un remount)
  if (typeof window !== 'undefined' && !window.__carteZoomed && props.parcelCoords && props.parcelCoords.length >= 3) {
    fitToParcel();
    window.__carteZoomed = true;
  }
  map.value = new maplibregl.Map({
    container: mapContainer.value,
    style: 'https://api.maptiler.com/maps/streets/style.json?key=tYoEcARxXl5IYrsQY5Tt',
    center: center,
    zoom: zoom,
    minZoom: 5,
    maxZoom: 33,
  });

  map.value.addControl(new maplibregl.NavigationControl());

  map.value.on('load', async () => {
    emit('update:loading', true);


    const colors = [
      '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
      '#ffff33', '#a65628', '#f781bf', '#999999', '#66c2a5',
      '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f',
    ];

    const layerColors = {
      'aif': '#e41a1c',
      'air_proteges': '#377eb8',
      'dpl': '#4daf4a',
      'dpm': '#984ea3',
      'enregistrement individuel': '#ff7f00',
      'litige': '#ffff33',
      'restriction': '#a65628',
      'tf_demembres': '#f781bf',
      'tf_en_cours': '#999999',
      'tf_etat': '#66c2a5',
      'titre_reconstitue': '#fc8d62',
      'zone_inondable': '#8da0cb',
      'parcelles': '#1b5e20'
    };
    // Utiliser la prop couchesDisponibles passée par le parent (couches ayant OUI)
    const couchesDisponibles = Array.isArray(props.couchesDisponibles) && props.couchesDisponibles.length > 0
      ? props.couchesDisponibles
      : [];


    // Générer la liste des fichiers geojson à partir de toutes les couches disponibles
    const geojsonAllLayers = allLayerIds.map(nom => `${nom}.geojson`);
    // Générer la liste des fichiers geojson à partir des couches par défaut (pour le parent)
    const geojsonCouchesDisponibles = couchesDisponibles.map(nom => `${nom}.geojson`);

    // Émettre la liste des couches à afficher par défaut au parent
    emit('init-layers', geojsonCouchesDisponibles.map(f => f.replace(/\.geojson$/i, '')));

    await Promise.all(geojsonAllLayers.map(async (filename, i) => {
      try {
        const url = `/${encodeURI(filename)}`;
        // Vérifier si le fichier existe avant de le charger
        const response = await fetch(url);
        if (!response.ok) return; // Ignore si le fichier n'existe pas
        const data = await response.json();
        const id = filename.replace(/\.geojson$/i, '');
        // Prendre la couleur de layerColors si elle existe, sinon fallback
        const color = layerColors[id] || colors[i % colors.length];

        if (map.value.getSource(id)) return;

        map.value.addSource(id, { type: 'geojson', data });

        map.value.addLayer({
          id: `${id}-fill`,
          type: 'fill',
          source: id,
          paint: { 'fill-color': color, 'fill-opacity': 0.5 },
        });

        map.value.addLayer({
          id: `${id}-line`,
          type: 'line',
          source: id,
          paint: { 'line-color': color, 'line-width': 2 },
        });
      } catch (e) {
        console.error(`Erreur lors du chargement du fichier ${filename}:`, e);
      }
    }));

    // Juste après le chargement initial, forcer la visibilité uniquement sur les couches par défaut
    allLayerIds.forEach(id => {
      const isVisible = couchesDisponibles.includes(id);
      if (map.value.getLayer(`${id}-fill`)) {
        map.value.setLayoutProperty(`${id}-fill`, 'visibility', isVisible ? 'visible' : 'none');
        map.value.setLayoutProperty(`${id}-line`, 'visibility', isVisible ? 'visible' : 'none');
      }
    });

    // Ajouter source pour la parcelle
    if (!map.value.getSource('parcel')) {
      map.value.addSource('parcel', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'Polygon',
            coordinates: [props.parcelCoords],
          },
        },
      });

      // remplissage
      map.value.addLayer({
        id: 'parcel-fill',
        type: 'fill',
        source: 'parcel',
        paint: {
          'fill-color': '#0D5C63', // sarcelle
          'fill-opacity': 0.4,
        },
      });

      // contour
      map.value.addLayer({
        id: 'parcel-line',
        type: 'line',
        source: 'parcel',
        paint: {
          'line-color': '#0D5C63',
          'line-width': 3,
        },
      });
    }

    updateParcel(props.parcelCoords); // dessiner la parcelle par défaut
    emit('update:loading', false);
  });
});

// 🔹 Fonction pour mettre à jour la parcelle
const updateParcel = (coords) => {
  if (!map.value || !map.value.getSource('parcel')) return;

  // Fermer le polygone automatiquement si ce n’est pas déjà fait
  const closedCoords =
    coords.length > 2 && coords[0] !== coords[coords.length - 1]
      ? [...coords, coords[0]]
      : coords;

  map.value.getSource('parcel').setData({
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [closedCoords],
    },
  });

  // Ajuster la vue sur la parcelle
  const bounds = closedCoords.reduce(
    (b, coord) => b.extend(coord),
    new maplibregl.LngLatBounds(closedCoords[0], closedCoords[0])
  );
  map.value.fitBounds(bounds, { padding: 40 });
};

// 🔹 Watch : redessiner si les coords changent
watch(
  () => props.visibleLayers,
  (val) => {
    console.log('[Carte.vue] visibleLayers changed:', val);
    updateLayerVisibility();
  },
  { deep: true, immediate: true }
);

// 🔹 Watch : redessiner si les coords changent

// Watch sur shouldDrawParcel : si true, dessine et zoome sur la parcelle
watch(() => props.shouldDrawParcel, (val) => {
  if (val && props.parcelCoords && props.parcelCoords.length >= 3) {
    updateParcel(props.parcelCoords);
    fitToParcel();
  }
});
</script>

<style scoped>
.map-controls {
  position: absolute;
  bottom: 20px;
  left: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10;
}

.zoom-button {
  background: white;
  border: none;
  border-radius: 4px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  opacity: 0.9;
}

.zoom-button:hover {
  background-color: #f8f9fa;
  transform: scale(1.05);
  opacity: 1;
}

.zoom-button:active {
  transform: scale(0.95);
}

.zoom-button svg {
  width: 20px;
  height: 20px;
  color: #333;
}

.map-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.mapboxgl-canvas {
  outline: none;
}

.recenter-button {
  background: white;
  border: none;
  border-radius: 4px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  z-index: 10;
  transition: all 0.2s ease;
  opacity: 0.9;
}

.recenter-button:hover {
  background-color: #f8f9fa;
  transform: scale(1.05);
  opacity: 1;
}

.recenter-button:active {
  transform: scale(0.95);
}

.recenter-button svg {
  width: 20px;
  height: 20px;
  color: #333;
}
</style>
