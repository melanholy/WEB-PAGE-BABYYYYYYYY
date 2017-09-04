var path = require('path');
var HtmlWebpackPlugin = require('html-webpack-plugin');

var DIST_DIR = path.resolve(__dirname, '../static') + '/';
var SRC_DIR = path.resolve(__dirname, 'src') + '/';

module.exports = {
    entry: SRC_DIR + 'index.jsx',
    output: {
        path: DIST_DIR,
        filename: '[hash].bundle.js',
        publicPath: '/static'
    },
    module: {
        loaders: [
            {
                test: /\.jsx$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: {
                    presets: [
                        "es2015", "react"
                    ]
                }
            },
            { test: /\.css$/, loader: 'style-loader!css-loader' }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            filename: '../index.html',
            template: 'index.ejs'
        })
    ]
};
