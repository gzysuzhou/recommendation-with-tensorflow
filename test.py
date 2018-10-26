from mysql import Mysql

res = Mysql().getAll("select * from post limit 10")

print(res)
