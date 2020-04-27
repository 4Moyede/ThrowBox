module.exports = {
  lintOnSave: true,
  transpileDependencies: ['vuetify'],

  // options...
  devServer: {
    proxy: 'https://localhoust:8000/',
  },
};
