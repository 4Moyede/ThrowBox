<template>
  <v-sheet style="margin-top: 70px">

    <!-- Loading Progress -->
    <v-overlay v-model="loadingData">
      <v-progress-circular :size="120" width="10" color="primary" indeterminate></v-progress-circular>
      <div style="color: #ffffff; font-size: 18px; margin-top: 10px">Loading Files...</div>
    </v-overlay>
    <!--  -->

    <!-- Add folder Dialog -->
    <v-dialog v-model="addFolderDialog" max-width="400">
      <v-card max-width="400" elevation="0" class="pa-4">
        <v-row justify="space-between" class="mx-0">
          <div class="dialogTitle">Add Folder</div>
          <v-btn class="mt-n1" icon @click="addFolderDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-row>
        <v-text-field
          class="mb-1 mt-3"
          label="Folder name"
          placeholder="Please Write Name"
          color="secondary"
          v-model="folderName"
        ></v-text-field>
        <v-row justify="end" class="mx-0">
          <v-btn color="secondary" @click="uploadFolder">Create</v-btn>
          <v-btn class="ml-3" @click="folderName = ''">clear</v-btn>
        </v-row>
      </v-card>
    </v-dialog>
    <!--  -->

    <!-- Upload Progress -->
    <v-overlay v-model="uploadProgress">
      <v-progress-circular :size="120" width="10" color="primary" indeterminate></v-progress-circular>
      <div style="color: #ffffff; font-size: 18px; margin-top: 10px">Uploading File...</div>
    </v-overlay>
    <!--  -->

    <!-- Data Table -->
    <v-card
      elevation="0"
      class="pa-5"
      min-height="900"
      @dragover.prevent
      @dragenter.prevent
      @drop.prevent="onDrop"
    >
      <v-data-table
        :headers="tableHeaders"
        :items="loadedFiles"
        class="elevation-0"
        :search="search"
        item-key="name"
        :sort-by="currentPage.sort"
        :sort-desc="currentPage.isRecent"
      >
        <!-- Top Setting -->
        <template v-slot:top>
          <v-row justify="space-between" class="mx-0 mt-n1 mb-2">
            <div style="font-size: 22px; font-weight: 500; color: #343a40">
              <v-icon color="grey800" size="30" class="mx-n2 mt-n1">mdi-power-on</v-icon>
              {{currentPage.title}}
            </div>
          </v-row>
        </template>
        <!--  -->

        <!-- Header Setting -->
        <template v-if="currentPage.title==='Storage'" v-slot:header="{ props: { headers } }">
          <thead>
            <tr>
              <th :colspan="headers.length">
                <v-row justify="end" class="mr-n3 ml-0 mt-n1">
                  <v-row justify="start" class="ml-n3">
                    <div v-for="(path, i) in pathArray" :key="i">
                      <v-row class="mx-0" v-if="i < pathArray.length-1">
                        <v-btn text class="pathBtnStyle" @click="moveSubFolderPath(path)">
                          <div>{{path.name}}</div>
                        </v-btn>
                        <v-icon>mdi-menu-right</v-icon>
                      </v-row>
                      <v-btn
                        @click="moveSubFolderPath(path)"
                        class="pathBtnStyle"
                        v-else
                        outlined
                        elevation="0"
                        color="primary"
                      >
                        <div>{{path.name}}</div>
                      </v-btn>
                    </div>
                  </v-row>
                  <v-btn class="mt-1" icon color="primary" @click="addFolderDialog = true">
                    <v-icon size="28">mdi-folder-plus</v-icon>
                  </v-btn>
                </v-row>
              </th>
            </tr>
          </thead>
        </template>
        <!--  -->

        <!-- Table Body Setting -->
        <template v-slot:body="{ items }">
          <tbody>
            <tr v-for="item in items" :key="item.name" @dblclick="clickFile(item)">
              <td>
                <v-row class="ml-n1">
                  <v-icon
                    color="primary"
                    style="margin-top:-2px; margin-right: 4px"
                    v-if="!item.isFile"
                  >mdi-folder-outline</v-icon>
                  <div v-else style="margin-top:-2px; margin-right: 4px">
                    <v-icon v-if="checkFileFormat(item.name) === 'image'">mdi-image-frame</v-icon>
                    <v-icon v-if="checkFileFormat(item.name) === 'video'">mdi-movie-outline</v-icon>
                    <v-icon
                      v-if="checkFileFormat(item.name) === 'docs'"
                    >mdi-file-document-edit-outline</v-icon>
                    <v-icon v-if="checkFileFormat(item.name) === 'zip'">mdi-egg</v-icon>
                    <v-icon v-if="checkFileFormat(item.name) === 'file'">mdi-file</v-icon>
                  </div>
                  <div class="fileNameStyle">{{item.name}}</div>
                </v-row>
              </td>
              <td>
                <div class="createdDateStyle" style="text-align: end">{{item.createdDate}}</div>
              </td>
              <td>
                <div class="fileSizeStyle" style="text-align: end">{{getfileSize}}</div>
              </td>
              <td v-if="currentPage.title !== 'Recycle bin'">
                <div style="text-align: start">
                  <!-- <v-btn @click="clickStar(item)" class="ml-n7" icon color="primary">
                    <v-icon>mdi-star</v-icon>
                  </v-btn> -->
                  <v-menu transition="slide-y-transition" bottom>
                    <template v-slot:activator="{ on }">
                      <v-btn icon class="ml-n6" v-on="on">
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
              </td>
            </tr>
          </tbody>
        </template>
        <!--  -->
      </v-data-table>
      <v-divider />

      <!-- File Specific -->
      <v-dialog v-model="fileSpecificDialog" max-width="500">
        <v-card elevation="0" outlined max-width="500">
          <v-row class="mx-3 mt-3 mb-1" justify="space-between">
            <div class="dialogTitle">File Specific</div>
            <v-btn icon @click="fileSpecificDialog = false">
              <v-icon size="28">mdi-close</v-icon>
            </v-btn>
          </v-row>
          <v-divider></v-divider>
          <v-row class="mt-2 mx-0">
            <v-col cols="4">
              <div class="dialogSubtitle">Name</div>
            </v-col>
            <v-col cols="8">
              <div class="dialogContents">{{fileSpecific.name}}</div>
            </v-col>
          </v-row>
          <v-row class="mt-n1 mx-0">
            <v-col cols="4">
              <div class="dialogSubtitle">Owner</div>
            </v-col>
            <v-col cols="8">
              <div class="dialogContents">{{fileSpecific.author}}</div>
            </v-col>
          </v-row>
          <v-row class="mt-n1 mx-0">
            <v-col cols="4">
              <div class="dialogSubtitle">Created Date</div>
            </v-col>
            <v-col cols="8">
              <div class="dialogContents">{{fileSpecific.createdDate}}</div>
            </v-col>
          </v-row>
          <v-row class="mt-n1 mx-0">
            <v-col cols="4">
              <div class="dialogSubtitle">Path</div>
            </v-col>
            <v-col cols="8">
              <div class="dialogContents">{{convertPath}}</div>
            </v-col>
          </v-row>
          <v-row class="mt-n1 mx-0">
            <v-col cols="4">
              <div class="dialogSubtitle">Size</div>
            </v-col>
            <v-col cols="8">
              <div class="dialogContents">{{getfileSize}}</div>
            </v-col>
          </v-row>
          <v-row class="mx-0 mt-4" justify="end" v-if="currentPage.title !== 'Recycle bin'">
            <v-btn class="mr-3" color="secondary">
              <a @click.prevent="downloadFile(fileSpecific.fid)" style="color: #ffffff">Download</a>
            </v-btn>
            <v-btn color="primary" class="mr-4">
              <a style="color: #ffffff">Share</a>
            </v-btn>
          </v-row>
          <v-row class="mx-0 mt-4" justify="end" v-else>
            <v-btn class="mr-4" color="secondary">
              <a @click.prevent="recoverFile(fileSpecific.fid)" style="color: #ffffff">Recover</a>
            </v-btn>
          </v-row>
          <div style="height: 15px"></div>
        </v-card>
      </v-dialog>
      <!--  -->

      <!-- Upload Button  -->
      <v-layout justify-center class="mt-8" v-if="currentPage.title==='Storage'">
        <v-btn color="primary" @click="clickUploadButton">Click or Drag & Drop</v-btn>
        <input ref="fileInput" style="display: none" type="file" @change="onFileChange" />
      </v-layout>
      <!--  -->

    </v-card>
  </v-sheet>
</template>

<script>
/* eslint-disable no-underscore-dangle */
// @ is an alias to /src

export default {
  name: 'DataTable',
  props: {
    search: {
      type: String,
      default: '',
    },
    loadedFiles: {
      type: Array,
      default: null,
    },
    userData: {
      type: Object,
      default: null,
    },
    currentPage: {
      type: Object,
      default: null,
    },
    loadingData: {
      type: Boolean,
      default: true,
    },
    tableParams: {
      type: Object,
      default: null,
    },
    tableHeaders: {
      type: Array,
      default: null,
    },
  },
  components: {},
  data() {
    return {
      folderName: '',
      pathArray: [],
      userInfo: {
        id: '',
        email: '',
      },
      uploadForm: [],
      fileSpecific: {},
      // dialog
      addFolderDialog: false,
      fileSpecificDialog: false,
      uploadProgress: false,
      actionNotify: false,

      // pagination & params
    };
  },
  // 초기 path ui를 구성하기 위한 작업.
  created() {
    if (this.currentPage.title === 'Storage') {
      this.pathArray.push({ name: 'root', path: this.tableParams.path });
    }
    console.log(this.pathArray);
  },
  computed: {
    // path
    convertPath() {
      let path = '/';
      this.pathArray.forEach((element) => {
        path += `${element.name}/`;
      });
      return path;
    },
    // file size
    getfileSize() {
      if (this.fileSpecific.fileSize === 0) {
        return '';
      }
      const s = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'];
      const e = Math.floor(Math.log(this.fileSpecific.fileSize) / Math.log(1024));
      return `${(this.fileSpecific.fileSize / 1024 ** e).toFixed(2)} ${s[e]}`;
    },
  },
  methods: {
    // 데이터 호출
    refreshData() {
      this.$emit('loadFiles');
    },
    // 폴더 이동 관련
    moveSubFolderPath(data) {
      this.tableParams.path = data.path;
      for (let i = 0; i < this.pathArray.length; i += 1) {
        const element = this.pathArray[i];
        if (element.path === data.path) {
          this.pathArray = this.pathArray.slice(0, i + 1);
          break;
        }
      }
      this.refreshData();
    },
    // 폴더 클릭 후 path 조정
    onClickFolder(data) {
      this.tableParams.path = data.fid;
      this.pathArray.push({ name: data.name, path: data.fid });
      this.refreshData();
    },

    // 파일 업로드 관련 drag & drop
    onDrop(event) {
      this.uploadFile(event.dataTransfer.files);
    },
    clickUploadButton() {
      this.$refs.fileInput.click();
    },
    onFileChange(event) {
      this.uploadFile(event.target.files);
    },
    // 파일 업로드
    uploadFile(files) {
      this.uploadProgress = true;
      console.log(files);
      const formData = new FormData();
      for (let i = 0; i < files.length; i += 1) {
        formData.append('file', files[i]);
        formData.append('name', files[i].name);
        formData.append('author', 'Tester');
        formData.append('path', this.tableParams.path);
        formData.append('isFile', true);
        formData.append('fileSize', files[i].size);
      }
      console.log(formData);
      this.$axios
        .post('/fileUpload/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        .then((r) => {
          this.uploadProgress = false;
          for (let index = 0; index < r.data.length; index += 1) {
            this.loadedFiles.push(r.data[index]);
          }
        })
        .catch((e) => {
          console.log(e.message);
        });
    },

    // 폴더 업로드
    uploadFolder() {
      if (this.folderName) {
        this.uploadProgress = true;
        const formData = new FormData();
        formData.append('name', this.folderName);
        formData.append('author', 'Tester');
        formData.append('path', this.tableParams.path);
        formData.append('isFile', false);
        formData.append('fileSize', 0);
        this.$axios
          .post('/folderUpload/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })
          .then((r) => {
            console.log(r);
            this.uploadProgress = false;
            this.folderName = '';
            this.addFolderDialog = false;
            this.loadedFiles.push(r.data);
          })
          .catch((e) => {
            console.log(e.message);
          });
      }
    },
    // 파일 및 폴더 클릭.
    clickFile(data) {
      if (data.isFile) {
        this.fileSpecific = data;
        this.fileSpecificDialog = true;
      } else {
        this.onClickFolder(data);
      }
    },
    // 파일 다운로드
    downloadFile(fileId) {
      this.$axios
        .get('/fileDownload/', {
          params: {
            fid: fileId,
          },
        })
        .then((r) => {
          const link = document.createElement('a');
          link.href = r.data.download_url;
          link.download = r.data.download_url;
          link.click();
          // window.location.assign(r.data.download_url);
          console.log(r.data.download_url);
        })
        .catch((e) => {
          console.log(e.message);
        });
    },
    // 파일 삭제
    deleteFile(data) {
      this.$axios
        .get('/fileTrash/', { file_id: data.fid })
        .then((r) => {
          this.actionNotify = true;
          console.log(r);
        })
        .catch((e) => {
          console.log(e.message);
        });
    },
    // 파일 복구
    recoverFile(fid) {
      this.$axios
        .get('/fileTrash/', { file_id: fid })
        .then((r) => {
          this.actionNotify = true;
          console.log(r);
        })
        .catch((e) => {
          console.log(e.message);
        });
    },
    // 이름 변경
    renameFile(data) {
      console.log(data);
    },
    // 즐겨찾기
    clickStar(data) {
      if (data.isFavorite) {
        console.log(1);
      } else {
        console.log(2);
      }
    },
    // 파일 포맷에 맞는 아이콘 설정
    checkFileFormat(format) {
      const fileFormat = format.slice(format.indexOf('.') + 1);
      if (
        fileFormat === 'jpg'
        || fileFormat === 'gif'
        || fileFormat === 'png'
        || fileFormat === 'svg'
        || fileFormat === 'bmp'
        || fileFormat === 'jpeg'
      ) {
        return 'image';
      }
      if (
        fileFormat === 'mp4'
        || fileFormat === 'avi'
        || fileFormat === 'mkv'
      ) {
        return 'video';
      }
      if (
        fileFormat === 'doc'
        || fileFormat === 'hwp'
        || fileFormat === 'ppt'
        || fileFormat === 'xlsx'
        || fileFormat === 'pdf'
        || fileFormat === 'xls'
        || fileFormat === 'docx'
      ) {
        return 'docs';
      }
      if (fileFormat === 'zip' || fileFormat === '7z' || fileFormat === 'rar') {
        return 'zip';
      }
      return 'file';
    },
  },
};
</script>

<style scoped>
.pathBtnStyle {
  text-transform: none !important;
}
.fileNameStyle {
  max-width: 600px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.createdDateStyle {
  white-space: nowrap;
}
.fileSizeStyle {
  white-space: nowrap;
}
.dialogTitle {
  color: #3f51b5;
  font-weight: 400;
  font-size: 20px;
}
.dialogSubtitle {
  margin-left: 14px;
  color: #343a40;
  font-weight: 500;
  font-size: 16px;
}
.dialogContents {
  color: #5a5a5a;
  font-weight: 400;
  font-size: 16px;
}
</style>
