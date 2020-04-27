import Vue from 'vue';
import Vuetify from 'vuetify/lib';

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#03A9F4',
        secondary: '#3F51B5',
        accent: '#00BCD4',
        error: '#F44336',
        info: '#2196F3',
        success: '#8BC34A',
        warning: '#FF5722',
        grey3: '#eceeef',
        grey5: '#aaa',
        grey7: '#5a5a5a',
        grey8: '#343a40',
      },
      dark: {
        primary: '#03A9F4',
        secondary: '#3F51B5',
        accent: '#00BCD4',
        error: '#F44336',
        info: '#2196F3',
        success: '#8BC34A',
        warning: '#FF5722',
        grey3: '#eceeef',
        grey5: '#aaa',
        grey7: '#5a5a5a',
        grey8: '#343a40',
      },
    },
  },
});
