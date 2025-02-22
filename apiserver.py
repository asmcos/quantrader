from flask import Flask,jsonify,request,Response
import json
from hk_eastmoney import get_stock_price_bylist 
app = Flask(__name__)

# 根路径
@app.route('/list')
def codelist():
    codelist = request.args.get("code")
    data = get_stock_price_bylist(codelist.split(","))
    return Response(
        json.dumps(data, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True)
