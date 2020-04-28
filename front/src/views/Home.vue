<template>
  <v-sheet style="margin-top: 70px">
    <v-card elevation="0" class="pa-5">
      <v-data-table
        :headers="tableHeaders"
        :items="files"
        class="elevation-0"
        :search="search"
        disable-pagination
        hide-default-footer
        :loading="dataLoading"
        item-key="name"
        :show-select="checkMultiSelectFile"
      >
        <!-- Header and Top Setting -->
        <template v-slot:top>
          <v-row justify="space-between" class="mx-0">
            <div>Storage</div>
            <v-icon>mdi-settings</v-icon>
          </v-row>
        </template>
        <template v-slot:header="{ props: { headers } }">
          <thead>
            <tr>
              <th :colspan="headers.length" style="font-size: 20px">Directory > Test1 > Test2</th>
            </tr>
          </thead>
        </template>

        <!-- Multiple Select Setting -->
        <template v-if="checkMultiSelectFile" v-slot:header.data-table-select="{ on, props }">
          <v-simple-checkbox color="purple" v-bind="props" v-on="on"></v-simple-checkbox>
        </template>

        <template
          v-if="checkMultiSelectFile"
          v-slot:item.data-table-select="{ isSelected, select }"
        >
          <v-simple-checkbox
            color="green" value="isSelected" @input="select($event)"></v-simple-checkbox>
        </template>

        <!-- Upload Loading Setting -->
        <template v-if="uploadProgress" v-slot:progress>
          <v-progress-linear color="primary" :height="15" indeterminate></v-progress-linear>
        </template>

        <!-- Table Body Setting -->
        <template v-slot:item.fileName="{ item }">
          <div @click="clickFile(item)" class="fileNameStyle">{{item.fileName}}</div>
        </template>

        <template v-slot:item.createdDate="{ item }">
          <div @click="clickFile(item)" class="createdDateStyle">{{item.createdDate}}</div>
        </template>

        <template v-slot:item.fileSize="{ item }">
          <div @click="clickFile(item)" class="fileSizeStyle">{{item.fileSize}}</div>
        </template>

        <template v-slot:item.action="{ item }">
          <div style="text-align: start">
            <v-btn class="ml-n7" icon color="orange">
              <v-icon>mdi-star</v-icon>
            </v-btn>

            <v-menu transition="slide-y-transition" bottom>
              <template v-slot:activator="{ on }">
                <v-btn icon class="ml-0" v-on="on">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item>
                  <v-list-item-title @click="renameFile(item)">Rename</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title @click="deleteFile(item)">Delete</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-data-table>
      <v-divider />
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
  components: {},
  data() {
    return {
      title: '',
      search: '',
      tableHeaders: [],
      files: [],
      dataLoading: false,
      uploadProgress: false,
      checkMultiSelectFile: false,
    };
  },
  methods: {
    uploadFile() {},
    clickFile(data) {
      console.log(data);
    },
    deleteFile() {

    },
    renameFile() {

    },
    initHeader() {
      this.tableHeaders = [
        { text: 'Name', value: 'fileName', align: 'left' },
        { text: 'Created', value: 'createDate', align: 'right' },
        { text: 'Size', value: 'fileSize', align: 'right' },
        { value: 'action', align: 'center', sortable: false },
      ];
    },
    loadFiles() {
      this.files = [
        {
          fileName: 'Test1',
          createDate: '2019-10-11',
          fileSize: '39kb',
        },
        {
          fileName: 'Test2',
          createDate: '2019-10-13',
          fileSize: '139kb',
        },
        {
          fileName: 'Test3',
          createDate: '2019-12-11',
          fileSize: '394kb',
        },
        {
          fileName: 'Test4',
          createDate: '2019-12-13',
          fileSize: '392mb',
        },
        {
          fileName: 'Test5',
          createDate: '2019-12-15',
          fileSize: '3229kb',
        },
        {
          fileName:
            'Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6Test6',
          createDate: '2020-01-05',
          fileSize: '32mb',
        },
        {
          fileName: 'Test7',
          createDate: '2020-02-19',
          fileSize: '36kb',
        },
        {
          fileName: 'Test8',
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
.fileNameStyle {
}
.createdDateStyle {
}
.fileSizeStyle {
}
</style>
