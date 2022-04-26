<template>
  <v-container>
    <v-row class="mt-2">
      <v-col cols="1"></v-col>
      <v-col cols="11">
        <h1>Very cool blog post</h1>
        <p class="text-left">
          Some text about some VERY interesting topic.
          <br />
          <code class="block whitespace-pre overflow-x-scroll">
            from python import very_concisely_written_function
          </code>
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "home_page",

  data: () => ({}),

  components: {},
  mounted() {},
  methods: {},
};
</script>
