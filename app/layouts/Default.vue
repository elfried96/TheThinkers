<template>
    <main class="flex-grow">
        <slot />
    </main>
    <USlideover title="Chatbot" description="Posez toutes vos questions sur le foncier " close-icon="i-lucide-arrow-right" :ui ="{content:'max-w-5xl'}">
        <UButton icon="i-lucide-bot-message-square" size="xl" color="secondary" variant="solid"  class=" fixed bottom-5 rounded-full right-5 z-100"/>
        <!-- <UButton  icon="" size="md" color="secondary" variant="solid" class=" fixed bottom-5 right-5 z-100 btn-msg" label="Chat" /> -->

        <template #body>
            <UChatPalette>
                <UChatMessages :messages="chat.messages" :status="chat.status"
                    :user="{ side: 'left', variant: 'naked', avatar: { src: 'https://github.com/benjamincanac.png' } }"
                    :assistant="{ icon: 'i-lucide-bot' }">
                    <template #content="{ message }">
                        <!-- <MDC :value="getTextFromMessage(message)" :cache-key="message.id" unwrap="p" /> -->
                    </template>
                </UChatMessages>

                <template #prompt>
                    <UChatPrompt class="fixed bottom-0" v-model="input" icon="i-lucide-search" variant="naked" :error="chat.error"
                        @submit="handleSubmit" />
                </template>
            </UChatPalette>
        </template>
    </USlideover>
</template>
<script setup lang="ts">
import { Chat } from '@ai-sdk/vue'
import type { UIMessage } from 'ai'
import { getTextFromMessage } from '@nuxt/ui/utils/ai'

const messages: UIMessage[] = []
const input = ref('')

const chat = new Chat({
    messages
})

function handleSubmit(e: Event) {
    e.preventDefault()
    chat.sendMessage({ text: input.value })
    input.value = ''
}
</script>
<style>
/* .btn-msg {
  
} */
</style>