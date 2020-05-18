<template>
  <div>
    <v-overlay v-model="dataLoading">
      <v-progress-circular :size="120" width="10" color="primary" indeterminate></v-progress-circular>
      <div style="color: #ffffff; font-size: 18px; margin-top: 10px">Loading Files...</div>
    </v-overlay>
    <data-table
      :search="search"
      :loadedFiles="getFiles"
      :userData="userInfo"
      :currentPage="StoragePage"
      @loadFiles="requestFiles"
    />
  </div>
</template>

<script>
import DataTable from '../components/DataTable.vue';

export default {
  name: 'Home',
  props: {
    search: {
      type: String,
      default: '',
    },
  },
  components: { DataTable },
  data() {
    return {
      userInfo: {
        id: '',
        email: '',
      },
      getFiles: [],
      dataLoading: true,
      params: {
        path: 'root',
        search: '',
      },
      StoragePage: {
        isRecent: false,
        sort: 'name',
        title: 'Storage',
      },
    };
  },
  // watch: {
  //   search(newValue, oldValue) {
  //     console.log(newValue);
  //     console.log(oldValue);
  //   },
  // },
  async created() {
    // await this.loadUserInfo();
    await this.requestFiles();
  },
  methods: {
    // 데이터 로드
    loadUserInfo() {
      this.$axios
        .get('/userInfo/')
        .then((r) => {
          console.log(r);
        })
        .catch((e) => {
          console.log(e);
        });
    },
    requestFiles(param) {
      if (param !== undefined) { this.params = param; }
      this.$axios
        .get('/fileList/', { params: this.params })
        .then((r) => {
          this.getFiles = r.data;
          this.dataLoading = false;
          for (let i = 0; i < this.getFiles.length; i += 1) {
            if (!this.getFiles[i].isFile) {
              this.getFiles[i].name = ` ${this.getFiles[i].name}`;
            }
            // Favorite 초기
            // for (let j = 0; j < this.getFiles[i].favorite.length; j += 1) {
            //   const favAuthor = this.getFiles[i].favorite[j];
            //   if (favAuthor === this.userInfo.id) {
            //     this.getFiles[i].isFavorite = true;
            //   } else {
            //     this.getFiles[i].isFavorite = false;
            //   }
            // }
          }
        })
        .catch((e) => {
          console.log(e);
        });
    },
  },
};
</script>

<style scoped>

</style>
