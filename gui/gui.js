var express  = require('express');
var log = require('npmlog');
var app = express();
function date() { return new Date().toISOString(); }


///////////////// Server settings //////////////////
app.use(express.static(__dirname + '/public'));     // route base URL requests to /public/index.html
log.level = 'info';                       // set logging level


/////////////////// Start server ///////////////////
log.info(date(), "GUI server configuration completed");
app.listen(8080, () => {
       log.info(date(), "Dashboard app is listening on port 8080");
    });
