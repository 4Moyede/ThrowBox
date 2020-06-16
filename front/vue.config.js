module.exports = {
  lintOnSave: true,
  transpileDependencies: ['vuetify'],
  configureWebpack: {
    output: {
      path: `${__dirname}/cool-build`,
    },
  },
  devServer: {
    disableHostCheck: true,
  },
};
