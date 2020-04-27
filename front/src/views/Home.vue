<template>
  <v-sheet style="margin-top: 70px">
    <v-row class="ml-3 mr-2">
      <div style="margin-top: 20px">Link</div>
    </v-row>
    <v-card elevation="0" class="pa-5">
      <v-data-table
        :headers="tableHeaders"
        :items="files"
        class="elevation-0"
        disable-pagination
        hide-default-footer
      ></v-data-table>
      <v-divider/>
      <v-layout justify-center class="mt-8">
        <v-btn color="primary">Click or Drag & Drop</v-btn>
      </v-layout>
    </v-card>

  </v-sheet>
</template>

<script>
// @ is an alias to /src

export default {
  name: 'Home',
  components: {
  },
  data() {
    return {
      title: '',
      tableHeaders: [],
      files: [],
    };
  },
  methods: {
    initHeader() {
      this.tableHeaders = [
        { text: 'Name', value: 'name' },
        { text: 'Created', value: 'createDate' },
        { text: 'Size', value: 'fileSize' },
      ];
    },
    loadFiles() {
      this.files = [
        {
          name: 'Test1',
          createDate: '2019-10-11',
          fileSize: '39kb',
        },
        {
          name: 'Test2',
          createDate: '2019-10-13',
          fileSize: '139kb',
        },
        {
          name: 'Test3',
          createDate: '2019-12-11',
          fileSize: '394kb',
        },
        {
          name: 'Test4',
          createDate: '2019-12-13',
          fileSize: '392mb',
        },
        {
          name: 'Test5',
          createDate: '2019-12-15',
          fileSize: '3229kb',
        },
        {
          name: 'Test6',
          createDate: '2020-01-05',
          fileSize: '32mb',
        },
        {
          name: 'Test7',
          createDate: '2020-02-19',
          fileSize: '36kb',
        },
        {
          name: 'Test8',
          createDate: '2020-03-29',
          fileSize: '12kb',
        },
      ];
    },
  },

  created() {
    this.initHeader();
    this.loadFiles();
  },
};
</script>

<style scoped>

</style>
