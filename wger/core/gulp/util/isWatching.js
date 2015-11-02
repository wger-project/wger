var argv = require('yargs').argv;

// > gulp            // true
// > gulp watch      // true
// > gulp build      // false
// > gulp <whatever> // false
module.exports = argv._.length === 0 || argv._[0] === 'watch' ? true : false;
