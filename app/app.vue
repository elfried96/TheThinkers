<template>
  <UApp>
    <NuxtLayout >
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
<style>
html, body {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  width: 100%;
  font-family: Inter, sans-serif;
}

/* Assure que le contenu principal prend toute la hauteur disponible */
#__nuxt {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
