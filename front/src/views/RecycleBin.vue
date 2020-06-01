<template>
  <div>
    <data-table
      :search="search"
      :loadedFiles="getFiles"
      :loadingData="dataLoading"
      :userData="userInfo"
      :currentPage="StoragePage"
      :tableHeaders="headers"
      @loadFiles="requestFiles"
    />
  </div>
</template>

<script>
import moment from 'moment';
import DataTable from '../components/DataTable.vue';

export default {
  name: 'Recent',
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
        isRecent: true,
        sort: 'deletedDate',
        title: 'Recycle bin',
      },
      headers: [
        { text: 'Name', value: 'name', align: 'start' },
        { text: 'Deleted', value: 'deletedDate', align: 'end' },
        { text: 'Size', value: 'fileSize', align: 'end' },
      ],
    };
  },
  created() {
    // this.loadUserInfo();
    this.requestFiles();
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
              this.getFiles.splice(i, 1);
            }
            // fid to Date
            const convertDate = moment(parseInt(this.getFiles[i].fid.substring(0, 8), 16) * 1000).format('YYYY-MM-DD hh:MM');
            this.getFiles[i].createdDate = convertDate;
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
