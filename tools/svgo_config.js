// svgo.config.js
module.exports = {
    plugins: [
        {
            name: 'removeViewBox',
            active: false,
        },
        {
            name: "removeDimensions",
            active: true
        }
    ]
};
