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
        { text: 'Created', value: 'fid', align: 'end' },
        { text: 'Size', value: 'fileSize', align: 'end' },
        { value: 'action', align: 'center', sortable: false },
      ],
    };
  },
  created() {
    this.requestFiles();
  },
  computed: {
    ...mapGetters({
      getToken: 'getAccessToken',
    }),

  },
  methods: {
    requestFiles() {
      this.dataLoading = true;
      console.log(this.params);
      this.$axios
        .get('/fileList/', {
          params: this.params,
        })
        .then((r) => {
          this.$store.dispatch('commitTotalFileSize', r.data.totalSize);
          this.getFiles = r.data.fileList;
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
