httpProxy = require('http-proxy');

var URL = 'http://data.10jqka.com.cn';


server = httpProxy.createServer({ secure: false, target: URL }, function (req, res, proxy) {


  proxy.proxyRequest(req, res, { secure: false, target: URL });

})

server.on('proxyReq', function(proxyReq, req, res, options) {
  proxyReq.setHeader('Host','data.10jqka.com.cn');
});



server.on('proxyRes', function(proxyRes, req, res, options) {
    proxyRes.on('data', function () {
        // 同花顺有CROS 权限
        //res.setHeader('Access-Control-Allow-Origin', '*');
        //res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    });

});



console.log("Listening on port 8008")

server.listen(8008);
