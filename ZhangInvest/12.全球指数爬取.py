import requests

# http://push2.eastmoney.com/api/qt/stock/sse?fields=f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f171,f47,f86,f292&mpi=1000&invt=2&fltt=1&secid=100.DJIA
DJIA = "100.DJIA"
# http://push2.eastmoney.com/api/qt/stock/sse?fields=f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f171,f47,f86,f292&mpi=1000&invt=2&fltt=1&secid=100.NDX
NDX = "100.NDX"
# http://push2.eastmoney.com/api/qt/stock/sse?fields=f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f171,f47,f86,f292&mpi=1000&invt=2&fltt=1&secid=100.SPX
SPX = "100.SPX"
# http://push2.eastmoney.com/api/qt/stock/sse?fields=f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f171,f47,f86,f292&mpi=1000&invt=2&fltt=1&secid=1.000001
SZZS = "1.000001"
# http://push2.eastmoney.com/api/qt/stock/sse?fields=f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f171,f47,f86,f292&mpi=1000&invt=2&fltt=1&secid=0.399001
SZCZ = "0.399001"

stock_code = "100.DJIA"
url = f"http://push2.eastmoney.com/api/qt/stock/sse?fields=f58,f43,f169,f170&mpi=1000&invt=2&fltt=1&secid={stock_code}"

try:
    with requests.get(url, stream=True) as response:
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")