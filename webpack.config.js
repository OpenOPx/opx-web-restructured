var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
const MiniCSSExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  context: __dirname,
  //target: 'node',
  entry: './myapp/static/js/main.js',
  output: {
      path: path.resolve('./myapp/static/webpack_bundles/'),
      filename: "[name].js"
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new MiniCSSExtractPlugin({
      filename: "./styles.css",
    })
  ],
  resolve: {
    alias: {
      'vue': 'vue/dist/vue.js'
    }
  },
  module:{
     rules:[
         {
             test:/\.(s*)css$/,
             use:[MiniCSSExtractPlugin.loader, 'css-loader', 'sass-loader']
          }
      ]
   }
}