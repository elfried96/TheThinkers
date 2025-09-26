import { defineStore } from 'pinia'
import type { ExtractResponse } from '../types/api'

export interface ExtractResponseWithId extends ExtractResponse {
  id: string
}


function generateId() {
  return Math.random().toString(36).substring(2, 10) + Date.now().toString(36)
}

export const useExtractStore = defineStore('extract', {
  state: () => ({
    items: [] as ExtractResponseWithId[]
  }),
  actions: {
    addExtract(data: ExtractResponse) {
      const id = generateId()
      const item: ExtractResponseWithId = { ...data, id }
      this.items.push(item)
      localStorage.setItem('extracts', JSON.stringify(this.items))
      return id
    },
    loadExtracts() {
      const raw = localStorage.getItem('extracts')
      if (raw) {
        this.items = JSON.parse(raw)
      }
    },
    getById(id: string) {
      return this.items.find(item => item.id === id)
    }
  }
})
