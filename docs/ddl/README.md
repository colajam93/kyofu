## dump DDL

```
mysqldump -h 127.0.0.1 -u kyofu -p -d kyofu | sed 's/AUTO_INCREMENT=[0-9]\+ //' > kyofu.sql
```
