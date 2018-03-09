<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=default"></script>

# 计算Fama因子的方法
> 为了计算每天对应特定指数下的Fama因子 
 
>  dataset的结构如下：    

| date     |index    |MKT   |SMB   |HML   |
|----------|:-------:|:-----:|:--- :|-----:|
|2005-01-01|000001.SH|0.05   |0.4   | 0.7  |

## 分组
* 按照每月末市值大小进行排序，以50%分位数为界分成S和B两组
* 再根据每月末的账面市值比（1/PB）大小排序，分成L(30%),M(40%)和H(30%)
* 分别对S、B和L、M、H取交集，得到SL、SM、SH、BL、BM和BH六类
* 分组每月更改一次
  

> 市值分成两组,账面市值比分成三组是由于账面市值比具有更强的作用

## SMB
> 市值因子， 由于公司规模不同造成的风险溢价

SMB = 1/3 \* (SL + SM + SH) - 1/3 \* (BL + BM + BH)

## HML
> 账面市值比，由于账面价值比不同造成的风险溢价  

HML = 1/2 \* (SH + BH) - 1/2 \* (SL + BL)

## MKT
> 市场的超额收益

用benchmark的收益减去无风险利率（一般使用什么来代替呢？）

