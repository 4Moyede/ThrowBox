<template>
  <div>
    <data-table
      :search="search"
      :loadingData="dataLoading"
      :loadedFiles="getFiles"
      :userData="userInfo"
      :currentPage="StoragePage"
      :tableHeaders="headers"
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
        path: '',
        search: '',
        starred: 'True',
      },
      StoragePage: {
        isRecent: false,
        sort: 'name',
        title: 'Favorite',
      },
      headers: [
        { text: 'Name', value: 'name', align: 'start' },
        { text: 'Created', value: 'fid', align: 'end' },
        { text: 'Size', value: 'fileSize', align: 'end' },
        { value: 'action', align: 'center', sortable: false },
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
        .get('/fileStarred/', { params: this.params })
        .then((r) => {
          this.getFiles = r.data;
          this.dataLoading = false;
          for (let i = 0; i < this.getFiles.length; i += 1) {
            if (!this.getFiles[i].isFile) {
              this.getFiles[i].name = ` ${this.getFiles[i].name}`;
            }
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
