<template>
  <v-sheet style="margin-top: 60px">
    <v-card elevation="0" class="pa-5" min-height="900"
      @dragover.prevent
      @dragenter.prevent
      @drop.prevent="onDrop"
    >
      <v-data-table
        :headers="tableHeaders"
        :items="loadedFiles"
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
            <div style="font-size: 22px; font-weight: 500; color: #343a40">
              <v-icon color="grey800" size="30" class="mx-n3 mt-n1">mdi-power-on</v-icon>
              Storage</div>
            <v-btn icon>
              <v-icon>mdi-settings</v-icon>
            </v-btn>
          </v-row>
        </template>
        <template v-slot:header="{ props: { headers } }">
          <thead>
            <tr>
              <th :colspan="headers.length">
                <v-row justify="start" class="ml-n3">
                  <div v-for="(path, i) in testArray" :key="i" style="">
                    <v-row class="mx-0" v-if="i < testArray.length-1">
                      <v-btn text class="pathBtnStyle" @click="moveSubFolderPath(path)">
                        <div>{{path}}</div>
                      </v-btn>
                      <v-icon>mdi-menu-right</v-icon>
                    </v-row>
                    <v-btn @click="moveSubFolderPath(path)" class="pathBtnStyle" v-else outlined elevation="0" color="primary">
                      <div>{{path}}</div>
                    </v-btn>
                  </div>
                </v-row>
              </th>
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
            <v-btn @click="clickStar(item)" class="ml-n7" icon color="primary">
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
        <v-btn color="primary" @click="clickUploadButton">Click or Drag & Drop</v-btn>
        <input ref="fileInput" style="display: none" type="file" @change="onFileChange">
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
      testArray: [
        'Name',
        'Files',
        'Documents',
        'Downloads',
        'this',
        'isme',
      ],
      storagePath: '',
      pathArray: [],
      userInfo: {
        id: '',
        email: '',
      },
      uploadForm: [],
      search: '',
      tableHeaders: [
        { text: 'Name', value: 'fileName', align: 'left' },
        { text: 'Created', value: 'createDate', align: 'right' },
        { text: 'Size', value: 'fileSize', align: 'right' },
        { value: 'action', align: 'center', sortable: false },
      ],
      loadedFiles: [],
      dataLoading: false,
      uploadProgress: false,
      checkMultiSelectFile: false,
    };
  },
  methods: {
    // 데이터 로드
    loadUserInfo() {
      // this.$axios.get('/')
      //   .then((r) => {
      //     console.log(r);
      //   })
      //   .catch((e) => {
      //     console.log(e);
      //   });
    },
    loadFiles() {
      this.loadedFiles = [
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
      // this.$axios.get('/')
      //   .then((r) => {
      //     this.loadedFiles = r.data;
      //     for (let i = 0; i < this.loadedFiles.length; i += 1) {
      //       for (let j = 0; j < this.loadedFiles[i].favorite.length; j += 1) {
      //         const favAuthor = this.loadedFiles[i].favorite[j];
      //         if (favAuthor === this.userInfo.id) {
      //           this.loadFiles[i].isFavorite = true;
      //         } else {
      //           this.loadFiles[i].isFavorite = false;
      //         }
      //       }
      //     }
      //   })
      //   .catch((e) => {
      //     console.log(e);
      //   });
    },
    moveSubFolderPath(path) {
      this.storagePath = '';
      for (let i = 0; i < this.testArray.length; i += 1) {
        const element = this.testArray[i];
        this.storagePath += element;
        if (element === path) {
          this.testArray = this.testArray.slice(0, i + 1);
          break;
        }
        this.storagePath += ',';
      }
      // this.loadFiles();
    },
    onClickFolder(path) {
      this.storagePath += `,${path}`;
      this.pathArray.push(path);
      // this.loadFiles();
    },
    // 파일 업로드 관련
    onDrop(event) {
      this.uploadFile(event.dataTransfer.files);
    },
    clickUploadButton() {
      this.$refs.fileInput.click();
    },
    onFileChange(event) {
      this.uploadFile(event.target.files);
    },
    uploadFile(files) {
      for (let i = 0; i < files.length; i += 1) {
        this.uploadForm[i] = {
          file: files[i],
          title: files[i].name,
          author: this.userInfo.id,
          path: this.storagePath,
        };
      }
      console.log(this.uploadForm);
      // this.$axios.post('/upload', this.uploadForm, { headers: { 'Content-Type': 'multipart/form-data' } })
      //   .then((r) => {
      //     this.uploadProgress = true;
      //     console.log(r);
      //   })
      //   .catch((e) => {
      //     console.log(e.message);
      //   });
    },

    // 파일 선택 및 옵션
    clickFile(data) {
      console.log(data);
      // 파일일 경우, Dialog - 파일 상세 정보 및 다운로드 버튼
      // 폴더일 경우, path 변경 및 데이터 로드
      this.onClickFolder(data.fileName);
    },
    deleteFile(data) {
      console.log(data);
    },
    renameFile(data) {
      console.log(data);
    },
    clickStar(data) {
      if (data.isFavorite) {
        console.log(1);
      } else {
        console.log(2);
      }
    },
  },

  async created() {
    await this.loadUserInfo();
    await this.loadFiles();
  },
};
</script>

<style scoped>
.pathBtnStyle {
  text-transform: none !important;
}
.fileNameStyle {
}
.createdDateStyle {
}
.fileSizeStyle {
}
</style>
