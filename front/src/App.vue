<template>
  <v-app id="inspire">
    <v-app-bar elevation="1" flat fixed>
      <v-btn icon color="secondary" @click="clickDrawer">
        <v-icon>mdi-menu</v-icon>
      </v-btn>
      <v-toolbar-title style="color: #3F51B5">ThrowBox</v-toolbar-title>
      <v-text-field
        v-model="searchFile"
        style="max-width: 600px; margin-left: 95px"
        prepend-inner-icon="mdi-magnify"
        hide-details
        placeholder="Search"
        outlined
        color="secondary"
        filled
        full-width
        single-line
        @keydown="enterSearch"
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-btn v-if="$vuetify.breakpoint.xs" icon color="#3F51B5">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
      <v-btn @click="logOut()" icon color="#3F51B5">
        <v-icon>mdi-account-arrow-right</v-icon>
      </v-btn>
      <div
        @click="logOut()"
        v-if="!$vuetify.breakpoint.xs"
        style="color: #3F51B5; font-size: 18px"
      >Log Out</div>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" app absolute>
      <v-list style="margin-top: 60px">
        <v-list-item-group color="secondary" v-model="navIndex">
          <v-list-item v-for="(item, i) in navMenu" :key="i" :to="item.to">
            <v-list-item-icon>
              <v-icon v-text="item.icon"></v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title v-text="item.text"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <v-divider class="mx-3"></v-divider>

      <v-icon class="ml-4 mt-4">mdi-server</v-icon>
      <div class="mt-n6 mr-4" style="margin-left: 71px">
        <div class="mb-2">Capacity</div>
        <v-progress-linear color="info" height="10" value="40" striped></v-progress-linear>
        <div style="font-size: 14px" class="mt-2">Total 100GB, 40GB used</div>
      </div>
    </v-navigation-drawer>
    <v-content>
      <router-view :search="searchFile" />
    </v-content>
    <v-footer></v-footer>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      drawer: true,
      navIndex: 0,
      navMenu: [
        { text: 'Storage', icon: 'mdi-database', to: { path: '/' } },
        { text: 'Recent', icon: 'mdi-history', to: { path: '/recent' } },
        { text: 'Favorite', icon: 'mdi-star', to: { path: '/favorite' } },
        { text: 'Recycle Bin', icon: 'mdi-delete', to: { path: '/bin' } },
      ],
      searchFile: '',
    };
  },
  methods: {
    clickDrawer() {
      if (this.drawer) {
        this.drawer = false;
      } else {
        this.drawer = true;
      }
    },
    logOut() {},
    enterSearch() {
      console.log(this.searchFile);
    },
  },
};
</script>

<style>
a:link {
  text-decoration: none;
}
a:visited {
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
</style>
