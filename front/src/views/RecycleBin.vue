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
        {
          text: 'Name', value: 'name', align: 'start', sortable: false,
        },
        {
          text: 'Deleted', value: 'deletedDate', align: 'end', sortable: false,
        },
        {
          text: 'Size', value: 'fileSize', align: 'end', sortable: false,
        },
      ],
    };
  },
  created() {
    this.requestFiles();
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
          this.dataLoading = false;

          r.data.fileList.forEach((element) => {
            if (element.deletedDate !== null) {
              this.getFiles.push(element);
            }
          });
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
