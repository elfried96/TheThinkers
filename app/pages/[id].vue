<template>
  <div class="main-container">
    <UDrawer  title="Résultats" :overlay="false" class="absolute z-99 top-10 left-5">
      <UButton label="Résultats" color="neutral"  leading-icon="i-lucide-align-vertical-justify-end" />

      <template #body>
        <div class="overflow-y-auto max-h-[80vh]">
          <div class="p-2">
            <h4 class="text-sm font-semibold uppercase  mb-2 px-1">Couches actives</h4>
            <div class="flex flex-wrap gap-2 mb-3 text-md">
              <div 
                  v-for="layer in availableLayers.filter(l => couche_superposes && couche_superposes.some(c => c.id === l.id))" 
                  :key="layer.id" 
                  class="flex items-center px-3 py-1.5 bg-white rounded-sm shadow-xs border border-gray-50 hover:shadow-sm transition-shadow cursor-pointer"
                  @click="toggleLayer(layer.id)"
                >
                <div 
                  class="w-3 h-3 rounded-sm mr-2 flex-shrink-0" 
                  :style="{ 
                    backgroundColor: selectedLayers.includes(layer.id) ? layerColors[layer.id as keyof typeof layerColors] : '#f3f4f6',
                    border: selectedLayers.includes(layer.id) ? 'none' : '1px solid #e5e7eb'
                  }"
                ></div>
                <span class="text-sm font-medium text-gray-700 whitespace-nowrap">{{ layer.name }}</span>
              </div>
            </div>
          </div>

          <UButton label="Télécharger les résultats" color="secondary" class="my-2 w-full sm:w-auto text-center" />
          
          <div class="border-t border-gray-100 p-2 ">
            <h4 class="text-sm font-semibold  uppercase mb-2 px-1">Caractéristiques</h4>
            <ul class="space-y-1.5">
              <li v-for="info in parcelInfo.filter(i => i.active)" :key="info.id" class="text-sm font-medium px-2 py-1.5 bg-white flex items-start">
                <span class="mr-2">{{ info.message.split(' ')[0] }}</span>
                <span>
                  <template v-if="info.id === 'aif'">
                    La parcelle se situe dans une Aire d’Intérêt Forestier (AIF). Elle est soumise à des restrictions spécifiques en matière d’usage et d’exploitation.
                  </template>
                  <template v-else-if="info.id === 'air_proteges'">
                    La parcelle se trouve dans une aire protégée. Les activités y sont strictement réglementées et peuvent être interdites.
                  </template>
                  <template v-else-if="info.id === 'dpl'">
                    La parcelle empiète sur le Domaine Public Lagunaire (DPL). Ce domaine n’est pas cessible et reste inaliénable.
                  </template>
                  <template v-else-if="info.id === 'dpm'">
                    La parcelle se situe dans le Domaine Public Maritime (DPM). Aucun titre foncier privé ne peut y être établi.
                  </template>
                  <template v-else-if="info.id === 'enregistrement individuel'">
                    La parcelle est déjà enregistrée au nom d’un particulier. Toute transaction devra tenir compte du propriétaire existant.
                  </template>
                  <template v-else-if="info.id === 'litige'">
                    La parcelle est signalée comme étant en litige. Il est recommandé de vérifier la situation judiciaire avant toute démarche.
                  </template>
                  <template v-else-if="info.id === 'restriction'">
                    La parcelle est concernée par une restriction d’usage. Une autorisation spéciale peut être nécessaire avant tout projet.
                  </template>
                  <template v-else-if="info.id === 'tf_demembres'">
                    La parcelle provient d’un Titre Foncier démembré. Vérifiez les références du lot correspondant.
                  </template>
                  <template v-else-if="info.id === 'tf_en_cours'">
                    La parcelle fait l’objet d’une demande de Titre Foncier en cours de traitement. Le processus n’est pas encore finalisé.
                  </template>
                  <template v-else-if="info.id === 'tf_etat'">
                    La parcelle est déjà immatriculée au nom de l’État. Elle ne peut être attribuée à titre privé.
                  </template>
                  <template v-else-if="info.id === 'titre_reconstitue'">
                    Le Titre Foncier de la parcelle a été reconstitué. Vérifiez l’authenticité auprès des services fonciers compétents.
                  </template>
                  <template v-else-if="info.id === 'zone_inondable'">
                    La parcelle est située en zone inondable. Tout projet de construction doit respecter les normes de prévention des risques.
                  </template>
                  <template v-else>
                    Caractéristique détectée.
                  </template>
                </span>
              </li>
              <li v-if="!parcelInfo.some(i => i.active)" class="text-sm text-gray-400 italic px-2 py-1.5">
                Aucune caractéristique spécifique détectée
              </li>
            </ul>
          </div>
        </div>
      </template>
    </UDrawer>
    <UPopover arrow class="absolute z-99 top-20 left-5">
      <UButton label="Couches" color="neutral" leading-icon="i-lucide-layers"  />

      <template #content>
        <div class="filter-panel">
          <h3>Couches</h3>
          <div class="layers-grid">
            <div v-for="layer in availableLayers" :key="layer.id" class="layer-item">
              <input type="checkbox" :id="layer.id" :value="layer.id" v-model="selectedLayers">
              <label :for="layer.id">{{ layer.name }}</label>
            </div>
          </div>
        </div>
      </template>
    </UPopover>

    <div class="map-wrapper">
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-message">Chargement en cours...</div>
      </div>
      <Carte
        ref="carteRef"
        :visible-layers="selectedLayers"
        @update:loading="isLoading = $event"
        @init-layers="initLayers"
        :parcel-coords="parcelCoords"
        :couches-disponibles="couche_superposes.map(l => l.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useExtractStore } from '../stores/extract'

const isLoading = ref(true)
const route = useRoute()
const extractStore = useExtractStore()

onMounted(() => {
  extractStore.loadExtracts()
})

const extractId = computed(() => route.params.id as string)
const extractData = computed(() => extractStore.getById(extractId.value))
const parcelCoords = computed(() => {
  if (!extractData.value || !extractData.value.coordinates_wgs84) return []
  return extractData.value.coordinates_wgs84.map(coord => [coord.longitude, coord.latitude])
})

onMounted(async () => {
  await nextTick()
  isLoading.value = false
})

const availableLayers = ref([
  { id: 'aif', name: 'AIF' },
  { id: 'air_proteges', name: 'Aires Protégées' },
  { id: 'dpl', name: 'DPL' },
  { id: 'dpm', name: 'DPM' },
  { id: 'enregistrement individuel', name: 'Enregistrement Individuel' },
  { id: 'litige', name: 'Litige' },
  { id: 'restriction', name: 'Restriction' },
  { id: 'tf_demembres', name: 'TF Démembrés' },
  { id: 'tf_en_cours', name: 'TF en Cours' },
  { id: 'tf_etat', name: 'TF État' },
  { id: 'titre_reconstitue', name: 'Titre Reconstitué' },
  { id: 'zone_inondable', name: 'Zone Inondable' },
  { id: 'parcelles', name: 'Parcelles' },
]);


// Générer dynamiquement les couches superposées à partir des réponses OUI
const couche_superposes = computed(() => {
  if (!extractData.value) return [];
  // Liste des clés de couches à vérifier
  const coucheKeys = [
    'aif', 'air_proteges', 'dpl', 'dpm', 'enregistrement_individuel', 'litige', 'restriction',
    'tf_demembres', 'tf_en_cours', 'tf_etat', 'titre_reconstitue', 'zone_inondable', 'parcelles'
  ];
  const data = extractData.value as Record<string, any>;
  return coucheKeys
    .filter(key => data && data[key] === 'OUI')
    .map(key => {
      const found = availableLayers.value.find(l => l.id === key || l.id.replace(/_/g, ' ') === key);
      return found ? { id: found.id, name: found.name } : { id: key, name: key };
    });
});



// Définition des couleurs pour chaque couche
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


const selectedLayers = ref([] as string[]);
watch(couche_superposes, (newCouches) => {
  selectedLayers.value = newCouches.map(l => l.id);
}, { immediate: true });
let hasInitLayers = false;
function initLayers(ids: string[]) {
  if (!hasInitLayers) {
    selectedLayers.value.splice(0, selectedLayers.value.length, ...ids);
    hasInitLayers = true;
  }
}

// Messages dynamiques en fonction des caractéristiques de la parcelle
const parcelInfo = ref([
  { id: 'litige', message: '⚠️ La parcelle est dans une zone de litige', active: false },
  { id: 'zone_inondable', message: '🌊 La parcelle est dans une zone inondable', active: false },
  { id: 'air_proteges', message: '🛡️ La parcelle est dans une zone protégée', active: false },
  { id: 'restriction', message: '🚧 La parcelle est soumise à des restrictions', active: false },
  { id: 'aif', message: '🏗️ La parcelle est dans une zone d\'aménagement', active: false },
  { id: 'tf_etat', message: '🏛️ La parcelle est un terrain de l\'État', active: false },
  { id: 'titre_reconstitue', message: '📜 La parcelle a un titre reconstitué', active: false },
]);

// Fonction pour mettre à jour les informations de la parcelle
const updateParcelInfo = (activeLayers: string[]) => {
  parcelInfo.value = parcelInfo.value.map(info => ({
    ...info,
    active: activeLayers.includes(info.id)
  }));
};

// Mettre à jour les infos quand les couches sélectionnées changent
watch(selectedLayers, (newLayers) => {
  updateParcelInfo(newLayers);
}, { immediate: true });

const toggleLayer = (layerId: string) => {
  const index = selectedLayers.value.indexOf(layerId);
  if (index === -1) {
    selectedLayers.value.push(layerId);
  } else {
    selectedLayers.value.splice(index, 1);
  }
};
</script>

<style scoped>
html,
body {
  margin: 0;
  padding: 0;
  min-height: 100%;
  width: 100%;
  overflow: hidden;
}

.main-container {
  position: relative;
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.filter-panel {
  max-width: 300px;
  padding: 0.5rem;
  /* background-color: #fffffa;
  overflow-y: auto; */
  font-size: 0.80rem;
  
}

.filter-panel h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.filter-panel div {
  margin-bottom: 0.5rem;
}

.layers-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
  margin-top: 4px;
  padding: 0 8px;
}

.layer-item {
  display: flex;
  align-items: center;
  gap: 2px;
  white-space: nowrap;
  font-size: 0.7rem;
  line-height: 1.2;
  margin-bottom: 2px;
}

.layer-item input[type="checkbox"] {
  margin: 0;
}

.map-wrapper {
  flex-grow: 1;
  position: relative;
  /* Needed for the overlay */
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.loading-message {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
}
</style>