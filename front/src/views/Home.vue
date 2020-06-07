<template>
  <div>
    <data-table
      :search="search"
      :loadedFiles="getFiles"
      :loadingData="dataLoading"
      :userData="userInfo"
      :currentPage="StoragePage"
      :tableParams="params"
      :tableHeaders="headers"
      @loadFiles="requestFiles"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
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
        path: '',
        search: '',
      },
      StoragePage: {
        isRecent: false,
        sort: 'name',
        title: 'Storage',
      },
      headers: [
        { text: 'Name', value: 'name', align: 'start' },
        { text: 'Created', value: 'createDate', align: 'end' },
        { text: 'Size', value: 'fileSize', align: 'end' },
        { value: 'action', align: 'center', sortable: false },
      ],
    };
  },
  // watch: {
  //   search(newValue, oldValue) {
  //     console.log(newValue);
  //     console.log(oldValue);
  //   },
  // },
  created() {
    // await this.loadUserInfo();
    // 회원관리 api 완성 시 vuex에 저장된 rootPath.
    this.requestFiles();
  },
  computed: {
    ...mapGetters({
      getToken: 'getAccessToken',
    }),
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
    requestFiles() {
      this.dataLoading = true;
      this.$axios
        .get('/fileList/', {
          params: this.params,
        })
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
