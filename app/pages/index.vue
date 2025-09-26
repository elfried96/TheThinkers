<template>
  <div class="min-h-screen bg-gray-50 py-0 px-0">
    <div class="max-w-md mx-auto bg-white rounded-lg shadow-sm min-h-[calc(100vh-2rem)] flex flex-col">
      <!-- Header -->

      <div class="p-6  bg-secondary  flex align-center gap-5">
        <div class="flex justify-around w-25">
          <div class="h-10 w-10 bg-white "></div>
          <div class="h-10 w-7 bg-white "></div>
          <div class="h-10 w-4 bg-white "></div>
        </div>
        <div>
          <h2 class="text-2xl text-semibold text-white">MonCadastre</h2>
        </div>

      </div>
      <div class="p-6 border-b border-gray-200 flex-shrink-0">
        <h1 class="text-xl font-semibold text-gray-900 mb-2">Bonjour,</h1>
        <p class="text-sm text-gray-600">consultez dès maintenant vos parcelles. </p>
      </div>

      <!-- Main Content -->
      <div class="p-6 flex-1 overflow-y-auto">
        <h2 class="text-lg font-medium text-gray-900 mb-3">
          Ajoutez vos levées topographiques
        </h2>
        <p class="text-sm text-gray-600 mb-6">
          Utilisez un levé topographique géoréférencé (PDF) de parcelle pour en vérifier la disponibilité et la fiabilité ainsi que de nombreuses autres informations liées.
        </p>

        <!-- File Upload Section -->
        <UForm @submit="onSubmit" class="space-y-4">
          <div class="space-y-1">
            <UFileUpload v-model="file" :accept="acceptedFormats.join(',')" :max-size="maxFileSize" :multiple="false"
              @error="handleFileError" class="w-full">
              <template #default="slotProps">
                <div @click="() => slotProps.open()"
                  class="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors"
                  :class="[fileError ? 'border-error-300 bg-error-50' : validFile ? 'border-secondary-300 bg-secondary-50' : 'border-gray-300 hover:border-gray-400']">
                  <UIcon name="i-heroicons-document-arrow-up" class="w-8 h-8 mx-auto text-gray-400 mb-2" />
                  <p class="text-sm text-gray-600 mb-1">
                    {{ file ? file.name : 'Cliquer pour ajouter votre fichier' }}
                  </p>
                  <p class="text-xs text-gray-500">
                    <span class="font-medium">Taille du fichier maximale:</span><br>
                    <span class="font-medium">Format supporté:</span> PDF
                  </p>
                </div>
              </template>
            </UFileUpload>
          </div>

          <!-- Submit Button -->
          <UAlert v-if="uploadSuccess" color="secondary" variant="soft" icon="i-heroicons-check-circle"
            title="Fichier uploadé avec succès" />

          <!-- Error Message -->
          <UAlert v-if="fileError" color="error" variant="soft" :title="fileError" />

          <!-- Continue Button -->
          <UButton type="submit" color="secondary" size="lg" block :disabled="!canContinue" :loading="uploading"
            class="mt-6" :ui="{ base: 'rounded-lg' }">
            {{ uploading ? 'Upload en cours...' : 'Continuer' }}
          </UButton>
        </UForm>
      </div>

      <!-- History Section -->
      <div class="border-t border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Historique</h3>
        </div>
        <p class="text-sm text-gray-600 mb-4">
          Retrouvez vos dernières vérifications de levées topographiques
        </p>

        <UButton variant="outline" color="secondary" size="md" block class="mb-4" @click="loadHistory"
          :loading="loadingHistory">
          Télécharger la sélection
        </UButton>


        <div class="space-y-3">
          <div v-for="item in historyItems" :key="item.id"
            class="flex items-center space-x-3 p-2 rounded hover:bg-gray-50">
            <UCheckbox v-model="item.selected" />
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-600 truncate">{{ item.name }}</p>
              <p class="text-xs text-gray-500">{{ item.date }}</p>
            </div>
            <div class="flex space-x-2">
              <UButton size="sm" variant="ghost" color="secondary">
                Voir
              </UButton>
              <UButton size="sm" variant="ghost" color="secondary">
                Télécharger
              </UButton>
            </div>
          </div>
        </div>
      </div>

      <div class="p-4 text-center bg-secondary text-md text-white">
        &copy; 2025 Tous droits réservés

      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useExtractStore } from '../stores/extract'
import type { ExtractResponse } from '../types/api'

// Reactive state
const file = ref<File | null>(null)
const fileError = ref('')
const uploadSuccess = ref(false)
const uploading = ref(false)
const loadingHistory = ref(false)
const validFile = ref(false)

// File validation settings
const maxFileSize = 10 * 1024 * 1024 // 10MB
const acceptedFormats = [
  'application/pdf', '.pdf',
  'image/png', '.png',
  'image/jpeg', '.jpg', '.jpeg',
  'image/webp', '.webp'
]

// Watch for file changes to perform validation
const validateFile = (fileToValidate: File | null) => {
  fileError.value = ''
  uploadSuccess.value = false
  validFile.value = false

  if (!fileToValidate) {
    return
  }

  // Validate file type
  const isTypeValid = acceptedFormats.some(format =>
    fileToValidate.type === format ||
    fileToValidate.name.toLowerCase().endsWith(format)
  )


  if (!isTypeValid) {
    fileError.value = 'Format non supporté. Seuls PDF, PNG, JPG, JPEG, WEBP sont acceptés.'
    return
  }

  if (fileToValidate.size > maxFileSize) {
    fileError.value = `Fichier trop volumineux (max ${maxFileSize / 1024 / 1024} Mo).`
    return
  }

  validFile.value = true
}

// Watch for file changes to perform validation
watch(file, (newFile) => {
  validateFile(newFile)
})

// Computed
const canContinue = computed(() => {
  // Désactive si erreur, fichier invalide ou upload en cours
  return validFile.value && !uploading.value && !fileError.value && !!file.value
})

// History data
const historyItems = ref([
  {
    id: 1,
    name: 'Levée du 13 Janvier 2025, 10h30',
    date: '13/01/2025',
    selected: false
  },
  {
    id: 2,
    name: 'Levée du 12 Janvier 2025, 15h00',
    date: '12/01/2025',
    selected: false
  },
  {
    id: 3,
    name: 'Levée du 10 Janvier 2025, 09h20',
    date: '10/01/2025',
    selected: false
  }
])

// Methods
const handleFileError = (error: any) => {
  fileError.value = error.message || 'Une erreur est survenue.'
  validFile.value = false
}

const router = useRouter()
const extractStore = useExtractStore()

const onSubmit = async () => {
  if (!canContinue.value || !file.value) return

  uploading.value = true
  fileError.value = ''

  try {
    if (!file.value) {
      throw new Error('Aucun fichier sélectionné')
    }

    const formData = new FormData()
    formData.append('file', file.value)

    // 👉 $fetch parse automatiquement le JSON
    const data: ExtractResponse = await $fetch('http://localhost:8000/extract', {
      method: 'POST',
      body: formData,
    })

    // Ajout au store et localStorage, génération d'id unique
    const id = extractStore.addExtract(data)

    uploadSuccess.value = true
    // file.value = null

    // Redirection vers la page @[id].vue
    await router.push({ path: `/${id}` })

  } catch (error: any) {
    fileError.value = error.message || "Erreur lors de l'upload du fichier"
    validFile.value = false
  } finally {
    uploading.value = false
  }
}


const loadHistory = async () => {
  loadingHistory.value = true
  try {
    // Simulate API call to load history
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('History loaded')
  } catch (error) {
    console.error('Error loading history:', error)
  } finally {
    loadingHistory.value = false
  }
}

// Simulate file upload API
const simulateFileUpload = async (fileToUpload: File): Promise<void> => {
  console.log('Uploading file:', fileToUpload.name)
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simulate random success/failure for demo
      if (Math.random() > 0.2) { // 80% success rate
        resolve()
      } else {
        reject(new Error('Erreur serveur simulée lors de l\'upload'))
      }
    }, 2000)
  })
}
</script>

<style scoped>
/* Additional custom styles if needed */
</style>