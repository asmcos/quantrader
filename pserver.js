httpProxy = require('http-proxy');

var URL = 'https://hq.sinajs.cn';


server = httpProxy.createServer({ secure: false, target: URL }, function (req, res, proxy) {


  proxy.proxyRequest(req, res, { secure: false, target: URL });

})


server.on('proxyRes', function(proxyRes, req, res, options) {
    proxyRes.on('data', function () {

        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    });

});



console.log("Listening on port 8000")

server.listen(8000);
