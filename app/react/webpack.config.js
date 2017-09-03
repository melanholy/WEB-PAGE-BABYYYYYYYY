var path = require('path');

var DIST_DIR = path.resolve(__dirname, '../static') + '/';
var SRC_DIR = path.resolve(__dirname, 'src') + '/';

module.exports = {
    entry: SRC_DIR + 'index.jsx',
    output: {
        path: DIST_DIR,
        filename: 'bundle.js',
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
    }
};
