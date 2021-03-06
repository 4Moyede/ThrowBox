import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    userInfo: {
      accessToken: localStorage.getItem('accessToken'),
      userName: localStorage.getItem('userName'),
      profileIMG: localStorage.getItem('profileIMG'),
    },
    totalFileSize: null,
  },
  mutations: {
    getToken(state) {
      state.userInfo.accessToken = localStorage.getItem('accessToken');
      state.userInfo.userName = localStorage.getItem('userName');
      state.userInfo.profileIMG = localStorage.getItem('profileIMG');
    },
    delToken(state) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('userName');
      localStorage.removeItem('profileIMG');
      state.userInfo.accessToken = null;
      state.userInfo.userName = null;
      state.userInfo.profileIMG = null;
      window.location.replace('/signin');
    },
    loadTotalFileSize(state, data) {
      state.totalFileSize = data;
    },
  },
  getters: {
    getAccessToken: (state) => state.userInfo.accessToken,
    getUserName: (state) => state.userInfo.userName,
    getProfileIMG: (state) => state.userInfo.profileIMG,
    getTotalFileSize: (state) => state.totalFileSize,
  },
  actions: {
    commitGetToken: (context) => context.commit('getToken'),
    commitDelToken: (context) => context.commit('delToken'),
    commitTotalFileSize: (context, data) => context.commit('loadTotalFileSize', data),
  },
  modules: {
  },
});
