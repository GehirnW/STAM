
#短周期价量因子
## alpha1
![equation](http://latex.codecogs.com/gif.latex?r1%20%3D%20rank%28Delta%28Ln%28volume%29%2C1%29%29)

<img src="https://latex.codecogs.com/svg.latex?\Large&space; r2 = rank(\frac{close-open}{open})" />

<img src="https://latex.codecogs.com/svg.latex?\Large&space; alpha1 = -1 * Corr(r1,r2,6)" />

## alpha2
<img src="https://latex.codecogs.com/svg.latex?\Large&space; alpha2 = -1 * Delta(\frac{(close - low) -(high - close)}{high - low},1) " />

## alpha3
$$ temp = \begin{cases}
			0,& close = Delay(close,1) \\\
			close - Min(low,Delay(close,1)),& close > Delay(close,1)\\\
			close - Max(high,Decay(close,1)),& close < Decay(close,1)
			\end{cases}
			$$
			
$$alpha3 = Sum(temp,6)$$

## alpha4
$$ alpha4 = \begin{cases}
			-1,& Mean(close,8) + STD(close,8) < Mean(close,2)\\\
			1, & Mean(close,2) < Mean(close,8) - STD(close,8)\\\
			1, & \frac{volume}{Mean(volume,20)} > = 1\\\
			-1,& else
			\end{cases}
			$$ 

## alpha5
$$ r1 = TsRank(volume,5)$$

$$ r2 = TsRank(high,5) $$

$$ alpha5 = -1 * TsMax(Corr(r1,r2,5),3)$$
## alpha6
$$alpha6 = Rank(sign(Delta((open * 0.85 + high * 0.15),4))) $$

## alpha7
$$ r1 = Rank(Max((vwap - close),3))$$
$$ r2 = Rank(Min((vwap - close),3))$$
$$ r3 = Rank(delta(volume,3))$$
$$ alpha7 = (r1 + r2) * r3 $$

## alpha8
$$ alpha8 = Rank(-1 * Delta((\frac{high + low}{2}*0.2 + vwap * 0.8),4)) $$

## alpha9
$$ temp = (\frac{high + low}{2} - Delay(\frac{high + low}{2},1)) * \frac{high - low}{volume}$$
$$ alpha9 = SMA(temp,7,2) $$

## alpha10
$$ temp = \begin{cases}
			Std(ret,20),& ret < 0 \\\
			close,&else 
			\end{cases}
			 $$
$$ alpha10 = Rank(Max(temp^2,5))$$


## alpha11
$$ alpha11 = Sum(\frac{(close - low) - (high - close)}{high - low} * volume,6)$$

## alpha12
$$ r1 = Rank(open - \frac{Sum(vwap,10)}{10})$$
$$ r2 = Rank(Abs(close - vwap))$$
$$ alpha12 = r1 - r2$$

## alpha13
$$ alpha13 = \frac{high + low}{2} - vwap$$

## alpha14
$$ alpha14 = close -Delay(close,5)$$

## alpha15
$$ alpha15 = \frac{open}{Delay(close,1)} - 1$$

## alpha16
$$ corr = Corr(Rank(volume),rank(vwap),5)$$
$$ alpha16 = -1 * TsMax(Rank(corr),5)$$

## alpha17
$$ alpha17 = Rank((vwap - Max(vwap,15))^{Delta(close,5)}）$$

## alpha18
$$ alpha18 = \frac{close}{Delay(close,5)}$$

## alpha19
$$ alpha19 = \begin{cases}
				\frac{close - Delay(close5)}{Decay(close,5)},&close < Decay(close,5)\\\
				(\frac{close - Delay(close5)}{close},& close > Decay(close,5))\\\
								0,&else
								\end{cases}
								$$

## alpha20
$$ alpha20 = \frac{close - Delay(close,6)}{Delay(close,6)} $$

## alpha21(??)


## alpha22
$$ temp = \frac{close -Mean(close,6)}{Mean(close,6)}$$
$$ alpha22 = SMA((temp - Delay(temp,3)),12,1)$$

## alpha23
$$ temp = \begin{cases}
			STD(close,20),& close > Decay(close,1) \\\
			0,&else
			\end{cases}
			$$
$$ alpha23 = \frac{SMA(temp,20,1)}{SMA(STD(close,20),20,1)} $$

## alpha24
$$ alpha24 = SMA((close - Delay(close,5)),5,1)$$

## alpha25
$$ r1 = Rank(Delta(close,7))a$$
$$ r2 = Rank(DecayLinear(\frac{volume}{Mean(volume,20)},9))$$
$$ r3 = Rank(Sum(ret,250))$$
$$ alpha25 = -1 * r1 * (1 - r2) * (1 + r3)$$

## alpha26
$$ alpha26 = Mean(close,7) - close + Corr(vwap,Delay(close,5),230)$$

## alpha27
$$ temp1 = \frac{close - Delay(close,3)}{Delay(close,3)} * 100$$
$$ temp2 = \frac{close - Delay(close,6)}{Delay(close,6)} * 100$$
$$ alpha27 = WMA(temp1 + temp2,12)$$

## alpha28
$$ temp1 = \frac{close - TsMin(low,9)}{TsMax(high,9) - TsMin(Low,9)}$$
$$ temp2 = SMA(temp1,3,1)$$
$$ alpha28 = 3 * temp2c - 2* SMA(temp2,3,1)$$

## alpha29cas1
$$ alpha = \frac{close - Dealy(close,6)}{Delay(close,6)} * volume$$

## alpha30
$$ resi = RegResi(\frac{close}{Delay(close,1)},MKT,SMB,HML,60)$$
$$ alpha30 = WMA(resi^2,20)$$

## alpha31
$$ alpha31 = \frac{close - Mean(close,12)}{Mean(close,12)} $$

## alpha32
$$ corr = Corr(Rank(high),Rank(volume),3)$$
$$ alpha32 = -1 * SUM(Rank(corr),3)$$

## alpha33
$$ temp1 = Delay(TsMin(low,5),5) - TsMin(low,5)$$
$$ temp2 = \frac{Sum(ret,240) - Sum(ret,20)}{220}$$
$$ alpha33 = temp1 * Rank(temp2) * TsRank(volume,5)$$

## alpha34
$$ alpha34 = \frac{Mean(close,12)}{close}$$

## alpha35
$$ r1 = Rank(DecayLinear(Delta(open,1),15))$$
$$ corr = Corr(volume,open * 0.65 + DecayLinear(open,17) * 0.35,7) $$
$$ r2 = Rank(-1 * corral)$$
$$ alpha35 = Min(r1,r2)$$

## alpha36v
$$ corr = Corr(Rank(volume),Rank(vwap),6)$$
$$ alpha36 = Rank(Sum(corr,2))$$

## alpha37
$$ temp = Sum(open,5) * Sum(ret,5)$$
$$ alpha37 = -1 * Rank(temp -  Delay(temp,10))$$

## alpha38
$$ judge = (Mean(high,20) < high) $$
$$alpha38 = \begin{cases}
		-1 * Delta(high,2),&judge=True \\\  
		0,&else 
		\end{cases}
		$$

## alpha39
$$ r1 = Rank(DecayLinear(Delta(close,2),8))$$
$$ corr = Corr((vwap * 0.3 + open * 0.7),Sum(Mean(volume,180),37),14)$$
$$ r2 = Rank(DecayLinear(corr,12))$$
$$ alpha39 = (r1 - r2) * -1$$

## alpha40
$$ judge1 = (close > Delay(close,1))$$
$$ temp1 = \begin{cases}
		volumne,&judge1 = True \\\
		0,&else
		\end{cases}
		$$
$$ judge2 = (close <= Delay(close,1))$$
$$ temp2 = \begin{cases}
		volume,&judge2 = True \\\
		0,&else
		\end{cases}
		$$
$$ alpha40 = \frac{Sum(temp1,26)}{Sum(temp2,26)} * 100$$

## alpha41
$$ alpha41 = -1 * Rank(Max(Delta(vwap,3),5))$$

## alpha42
$$ r1 = Rank(STD(high,10))$$
$$ corr = Corr(high,volume,10)$$
$$ alpha42 = -1 * r1 * corr$$

## alpha43
$$ judge = (close < Delay(close,1)) $$
$$ temp = \begin{cases}
			-1 * volume,& judge = True \\\
			volume,& else
			\end{cases}
			$$
$$ alpha43 = Sum(temp,6)$$

## alpha44
$$ corr = Corr(low,Mean(volume,10),7)$$
$$ r1 = TsRank(DecayLinear(corr,6),4)$$
$$ r2 = TsRank(DecayLinear(Delta(vwap,3),10),15)$$
$$ alpha44 = r1 + r2$$

## alpha45
$$ r1 = Rank(Delta((close * 0.6 + open * 0.4),1))$$
$$ r2 = Rank(Corr(vwap,Mean(volume,150),15))$$
$$ alpha45 = r1 + r2$$

## alpha46
$$ alpha46 = \frac{Mean(close,3) + Mean(close,6) + Mean(close,12) + Mean(close,24)}{4 * close}$$

## alpha47
$$ temp = \frac{TsMax(high,6) - close}{TsMax(high,6) - TsMin(low,6)} * 100$$
$$ alpha47 = SMA(temp,9,1)$$

## alpha48
$$ temp1 = close - Delay(close,1)$$
$$ temp2 = Sign(temp1) + Sign(Delay(temp1,1)) + Sign(Delay(temp1,2))$$
$$ alpha48 = -1 * Rank(\frac{temp2 * Sum(volume,5)}{Sum(volume,20)})$$

## alpha49
$$ temp = \begin{cases}
					1, & high + low < Delay(high,1) + Delay(low,1) \\\
					0, & else
					\end{cases}$$
$$ alpha49 = Sum(temp,12)$$

## alpha50
$$ temp = \begin{cases}
				-1, &high + low <= Delay(high,1) + Delay(low,1) \\\
				1,else
				\end{cases}
				$$
$$ alpha50 = Sum(temp,12)$$

## alpha51
$$ temp = \begin{cases}
					0, & high + low <= Delay(high,1) + Delay(low,1) \\\
					1, & else
					\end{cases}$$
$$ alpha51 = Sum(temp,12)$$


## alpha52
$$ temp1 = Max(0,high - Delay(\frac{high + low + close}{3}),1)$$
$$ temp2 = Max(0,Delay(\frac{high + low + close}{3},1)- low)$$
$$ alpha52 = \frac{Sum(temp1,26)}{Sum(temp2,26)} * 100$$

## alpha53
$$ alpha53 = \frac{Count(close > Delay(close,1),12)}{12} * 100$$

## alpha54(??)
$$ temp = STD(abs(close - open) + (close - open),?) + Corr(close,open,10)$$
$$ alpha54 = -1 * Rank(temp)$$

## alpha55(???)
$$ temp1 = \frac{close - Delay(close,1) + \frac{close - open}{2} + Delay(close,1) - Delay(open,1}{abs(high - Delay(close,1))}$$
$$ judge1 = (abs(high - Delay(close,1)) > abs(high - Delay(low,1)))$$
$$ judge2 = (abs(low - Delay(close,1) > abs(high - Delay(close,1))))$$
$$ temp21 = abs(high - Delay(close,1)) + \frac{abs(low - Delay(close,1))}{2} + \frac{abs(Delay(close,1) - Delay(open,1))}{4}$$
$$ temp22 = abs(low - Delay(close,1)) $$
$$ temp31 = abs(low - Delay(close,1)) + \frac{abs(high - Delay(close,1))}{2} +\frac{abs(Delay(close,1) - Delay(open,1))}{4}$$
$$ temp32 = (abs(high - Delay(low,1)) + abs(Delay(close,1) - Delay(open,1))) * Max(abs(high - Delay(close,1)),abs(low - Delay(close,1)))$$
$$ temp5 = \begin{cases}
				(temp1 > abs(low - Delay(close,1))) & (temp21 > abs(high - Delay(low,1)) & (temp31 > abs(high - Delay(close,1)))),& temp1$$

## alpha56(??)
$$ r1 = Rank(open - TsMin(open,12))$$
$$ corr = Corr(Sum(\frac{high+low}{2},19),Sum(Mean(volume,40),19),13)$$
$$ alpha56 = (r1 < Rank(corr))$$

## alpha57
$$ temp = \frac{close - TsMin(low,9)}{TsMax(high,9) - TsMin(low,9)} * 100$$
$$ alpha57 = SMA(temp,3,1)$$

## alpha58
$$ alpha58 = \frac{Count(close > Delay(close,1),20)}{20} * 100$$

## alpha59
$$ temp = \begin{cases}
			0,& close = Delta(close,1) \\\
			Min(low,Delay(close,1)),& close > Delay(close,1)\\\
			Max(high,Delay(close,1)),& close < Delay(close,1)
			\end{cases}
			$$
$$ alpha59 = Sum(temp,20)$$

## alpha60
$$ alpha60 = Sum(\frac{(close - low) - (high - close)}{high - low} * volume,20)$$

## alpha61
$$ r1 = Rank(DecayLinear(Delta(vwap,1),12))$$
$$ r2 = Rank(DecayLinear(Corr(low,Mean(volume,80),8),17))$$
$$ alpha61 = Max(r1,r2) * -1$$

## alpha62 
$$ alpha62 = -1 * Corr(high,Rank(volume),5)$$

## alpha63
$$ temp1 =  max(close - Delay(close,1),0)$$
$$ temp2 = abs(close - Delay(close,1))$$
$$ alpha63 = \frac{SMA(temp1,6,1)}{SMA(temp2,6,1)} * 100$$

## alpha64
$$ r1 = Rank(DecayLinear(Corr(Rank(vwap),Rank(volume),4),4))$$
$$ r2 = Rank(DecayLinear(Max(Corr(Rank(close),Rank(Mean(close,60)),4),13),14))$$
$$ alpha64 = Max(r1,r2) * -1$$

## alpha65
$$ alpha65 = \frac{Mean(close,6)}{close}$$

## alpha66
$$ alpha66 = \frac{close - Mean(close,6)}{Mean(close,6)} * 100$$

## alpha67
$$ temp1 = Max(close - Delay(close,1),0)$$
$$ temp2 = Abs(close - Delay(close,1))$$
$$ alpha67 = \frac{SMA(temp1,24,1)}{SMA(temp2,24,1)} * 100$$

## alpha68
$$ temp = (\frac{high + low}{2} - (\frac{Delay(high,1)}{2} + \frac{Delay(low)}{2}))* \frac{high - low}{volume}$$
$$ alpha68 = SMA(temp,15,2)$$

## alpha69
$$ alpha69 = \begin{cases}
			\frac{Sum(DTM,20) - Sum(DBM,20)}{Sum(DTM,20)}, & Sum(DTM,20) > SUM(DBM,20)\\\
			\frac{Sum(DTM,20) - Sum(DBM,20)}{Sum(DBM,20)}, & Sum(DTM,20) < SUM(DBM,20)\\\
			0,else
			\end{cases}
			$$

## alpha70
$$ alpha70 = STD(amount,6)$$

## alpha71
$$ alpha71 = \frac{close - Mean(close,24)}{Mean(close,24)} * 100$$

## alpha72
$$ temp = \frac{TsMax(high,6) - close}{TsMax(high,6) - TsMin(low,6)} * 100$$
$$ alpha72 = SMA(temp,15,1)$$

## alpha73
$$ corr = Corr(close,volume,10)$$
$$ r1 = TsRank(DecayLinear(DecayLinear(corr,16),4),5)$$
$$ r2 = Rank(DecayLinear(Corr(vwap,Mean(volume,30),4),3))$$
$$ alpha73 = (r1 - r2) * -1$$

## alpha74
$$ r1 = Rank(Corr(Sum(low * 0.35 + vwap * 0.65,20),Sum(Mean(volume,40),20),7))$$
$$ r2 = Rank(Corr(Rank(vwap),Rank(volume),6))$$
$$ alpha74 = r1 + r2$$

## alpha75
$$ c1 = Count(((close > open) AND (benchClose < benchOpen)),50)$$
$$ c2 = Count((benchClose < benchOpen),50)$$
$$ alpha75 = \frac{c1}{c2}$$

## alpha76
$$ temp = abs(\frac{\frac{close}{Decay(close,1)} - 1}{volume})$$
$$ alpha76 = \frac{STD(temp,20)}{Mean(temp,20)}$$

## alpha77
$$ r1 = Rank(DecayLinear((\frac{high + low}{2} + high - (vwap + high)),20))$$
$$ r2 = Rank(DecayLinear(Corr(\frac{high + low}{2},Mean(volume,40),3),6))$$
$$ alpha77 = Min(r1,r2)$$

## alpha78
$$ temp1 = \frac{high + low + close}{3} $$
$$ alpha78 = \frac{temp - Mean(temp,12)}{0.015 * Mean(abs(close - Mean(temp,12)),12)}$$

## alpha79
$$ temp1 = Max(close - Delay(close,1),0)$$
$$ temp2 = abs(close - Delay(close,1))$$
$$ alpha79 = \frac{SMA(temp1,12,1)}{SMA(temp2,12,1)} * 100$$

## alpha80
$$ alpha80 = \frac{volume - Delay(volume,5)}{Delay(volume,5)} * 100$$

## alpha81
$$ alpha81 = SMA(volume,21,2)$$

## alpha82
$$ temp = \frac{TsMax(high,6) - close}{TsMax(high,6) - TsMin(low,6)} * 100$$
$$ alpha82 = SMA(temp,20,1)$$

## alpha83
$$ alpha83 = -1 * Rank(Cov(Rank(high),Rank(volume),5))$$

## alpha84
$$ temp = \begin{cases}
				volume, & close > Delta(close,1) \\\
				-volume, & close < Delta(close,1) \\\
				0,&else
				\end{cases}
				$$
$$ alpha84 = Sum(temp,20)$$

## alpha85
$$ r1 = TsRank(\frac{volume}{Mean(Volume,20)},20)$$
$$ r2 = TsRank((-1 * Delta(close,7)),8)$$
$$ alpha85 = r1 * r2$$

## alpha86
$$ temp = \frac{Delay(close,20) - Delay(close,10)}{10} - \frac{Delay(close,10) - close}{10}$$
$$ alpha86 = \begin{cases}
				-1,&temp> 0.25 \\\
				1,& temp < 0 \\\
				-1 * (close - Delay(close,1)),& else
				\end{cases}
				$$

## alpha87(??)
$$ r1 = Rank(DecayLinear(Delta(vwap,4),7))$$
$$ temp = \frac{low * 0.9 + high * 0.1 - vwap}{open - \frac{high + low}{2}}$$
$$ r2 = TsRank(DecayLinear(temp,11),7)$$
$$ alpha87 = (r1 + r2) * -1$$

## alpha88
$$ alpha88 = \frac{close - Delay(close,20)}{Delay(close,20)} * 100$$

## alpha89
$$ temp = SMA(close,13,2) - SMA(close,27,2) $$
$$ alpha89 = 2 * (temp - SMA(temp,10,2))$$

## alpha90
$$ alpha90 = Rank(Corr(Rank(vwap),Rank(volume),5)) * -1$$

## alpha91
$$ r1 = Rank(close - Max(close,5)$$
$$ r2 = Rank(Corr(Mean(volume,40),low,5))$$
$$ alpha91 = (r1 * r2) * -1$$

## alpha92
$$ r1 = Rank(DecayLinear(Delta(close * 0.35 + vwap * 0.65,2),3))$$
$$ temp = abs(Corr(Mean(volume,180),close,13))$$
$$ r2 = TsRank(DecayLinear(temp,5)),15)$$

## alpha93
$$ temp = \begin{cases}
				0,&open >= Decay(open,1) \\\
				Max(open - low,open -Delay(open,1)),&else
				\end{cases}
				$$
$$ alpha93 = Sum(temp,20)$$

## alpha94
$$ temp = \begin{cases}
				volume,& close > Delay(close,1) \\\
				-volume, & close < Delay(close,1) \\\
				0, & else
				\end{cases}
				$$
$$ alpha94 = Sum(temp,30)$$

## alpha95
$$ alpha95 = STD(amount,20)$$

## alpha96
$$ temp = \frac{close - TsMin(low,9)}{TsMax(high,9) - TsMin(low,9)} * 100$$
$$ alpha96 = SMA(SMA(temp,3,1),3,1)$$

## alpha97
$$ alpha97 = STD(volume,10)$$

## alpha98
$$ temp = \frac{Delta(Mean(close,100),100)}{Delay(close,100)}$$
$$ alpha98 = \begin{cases}
				-1 * (close - TsMin(close,100)),& temp >= 0.05 \\\
				-1 * Delta(close,3),else
				\end{cases}
				$$

## alpha99
$$ alpha99 = -1 * Rank(Cov(Rank(close),Rank(volume),5))$$

## alpha100
$$ alpha100 = STD(volume,20)$$

## alpha101
$$ temp = $$

## alpha102
$$ temp = volume - Delay(volume,1)$$
$$ alpha102 = \frac{SMA(Max(temp,0),6,1}{SMA(abs(temp),6,1)} * 100$$

## alpha103
$$ alpha103 = \frac{20 - Lowday(low,20)}{20} * 100$$

## alpha104
$$ alpha104 = -1 * Delta(Corr(high,volume,5),5) * Rank(STD(close,20))$$

## alpha105
$$ alpha105 = -1 * Corr(Rank(open),Rank(volume),10)$$

## alpah106
$$ alpha106 = close - Delay(close,20)$$

## alpha107
$$ alpha107 = -1 * Rank(open - Delay(high,1)) * Rank(open - Delay(close,1)) * Rank(open - Delay(low,1))$$

## alpha108
$$ r1 = Rank(high - Min(high,2))$$
$$ r2 = Rank(Corr(vwap,Mean(volume,120),6))$$
$$ alpha108 = r1 * r2 * -1$$

## alpha109
$$ temp = SMA(high - low,10,2)$$
$$ alpha109 = \frac{temp}{SMA(temp,10,2)}$$

## alpha110
$$ alpha110 = \frac{Sum(Max(0,high - Delay(close,1)),20)}{Sum(Max(0,Delay(close,1) - low),20)}$$

## alpha111
$$ temp = vol * \frac{(close - low) - (high - close)}{high - low}$$
$$ alpha111 = SMA(temp,11,2) - SMA(temp,4,2)$$

## alpha112
$$ temp = \begin{cases}
				0, & close > Delay(close,1) \\\
				1,else
				\end{cases}
				$$
$$ alpha112 = Sum(temp,12)$$

## alpha113
$$ r1 = Rank(Mean(Delay(close,5),20) * Corr(close,volume,2))$$
$$ r2 = Rank(Corr(Sum(close,5),Sum(close,20),2))$$
$$ alpha113 = r1 * r2 * -1$$

## alpha114(??)
$$ r1 = Rank(Delay(\frac{high - low}{Mean(close,5)},2))$$
$$ r2 = $$

## alpha115
$$ r1 = Rank(Corr(high * 0.9 + low * 0.1, Mean(volume,30),10))$$
$$ r2 = Rank(Corr(TsRank(\frac{high + low}{2},4),TsRank(volume,10),7))$$
$$ alpha115 = r1 * r2$$

## alpha116
$$ alpha1116 = RegBeta(close,sequence,20)$$

## alpha117
$$ alpha117 = TsRank(volume,32) * (1- RsRank(close + high - low,16)) * (1 - TsRank(ret,32))$$

## alpha118
$$ alpha118 = \frac{Sum(high - open,20)}{Sum(open - low,20)} * 100$$

## alpha119
$$ corr1 = Corr(vwap,Sum(Mean(volume,5),26),5)$$
$$ corr2 = Corr(Rank(open),Rank(Mean(volume,15)),21)$$
$$ alpha119 = Rank(DecayLinear(corr1,7)) - Rank(DecayLinear(TsRank(Min(corr,9),7),8))$$

## alpha120
$$ alpha120 = \frac{Rank(vwap - close)}{Rank(vwap + close)}$$

## alpha121
$$ temp = TsRank(Corr(TsRank(vwap,20),TsRank(Mean(volume,60),2),18),3)$$
$$ alpha121 = Rank(vwap - Min(vwap,12)) ^ {temp} * -1$$

## alpha122 
$$ temp1 = SMA(Ln(close),13,2)$$
$$ temp2 = SMA(SMA(SMA(temp1,13,2),13,1),13,1)$$
$$ alpha122 = \frac{temp2}{Delay(temp2,1)}$$

## alpha123
$$ corr1 = Corr(Sum(\frac{high + low}{2},20),Sum(Mean(volume,60),20),9)$$
$$ corr2 = Corr(low,volume,6)$$
$$ alpha123 = (Rank(corr1) < Rank(corr2)) * -1$$

## alpha124
$$ alpha124 = \frac{close - vwap}{DecayLinear(Rank(TsMax(close,30),2))}$$

## alpha125
$$ temp1 = Corr(vwap, Mean(volume,80),17)$$
$$ temp2 = Delta(close * 0.5 + vwap * 0.5,3)$$
$$ alpha125 = \frac{Rank(DecayLinear(temp1,20))}{Rank(DecayLinear(temp2,16))} $$

## alpha126
$$ alpha126 = \frac{close + hig+ low}{3}$$

## alpha127
$$ alpha127 = \frac{close - Max(close,12)}{Maxx(close,12)}$$

## alpha128
$$ temp1 = \frac{high + low + close}{3}  $$
$$ temp2 = \begin{cases}
				temp1 * volume,&temp1 > Delay(temp,1) \\\
				0,else
				\end{cases}
				$$
$$ temp3 = \begin{cases}
				0,&temp1 > Delay(temp,1)\\\
				temp1,else
				\end{cases}
				$$
$$ alpha128 = 100 - \frac{100}{1 + \frac{Sum(temp2,14)}{Sum(temp3,14)}}$$

## alpha129
$$ temp = \begin{cases}
				0 ,& close -  Delay(close,1) < 0\\\
				abs(close - Delay(close,1),& else
				\end{cases}
				$$
$$ alpha129 = Sum(temp,12)$$

## alpha130
$$ corr1 = Corr(\frac{high + low}{2},Mean(volume,40),9)$$
$$ corr2 = Corr(Rank(close),Rank(volume),7)$$
$$ alpha130 = \frac{Rank(DecayLinear(corr1,10))}{Rank(DecayLinear(corr2,3))}$$

## alpha131
$$ corr = Corr(close,Mean(volume,50),18)$$
$$ alpha131 = 	Rank(Delta(vwap,1)^{TsRank(corr,18)})$$

## alpha132
$$ alpha132 = Mean(amount,20)$$

## alpha133
$$ alpha133 = (20 - \frac{Highday(high,20)}{20}) * 100 - (20 - \frac{Lowday(low,20)}{20}) * 100$$

## alpha134
$$ alpha134 = \frac{close - Delay(close,12)}{Delay(close,12)} * volume$$

## alpha135
$$ alpha135 = SMA(Delay(\frac{close}{Delay(close,20)},1),20,1)$$

## alpha136
$$ alpha136 = -1 * Rank(Delta(ret,3)) * Corr(open,volume,10)$$

## alpha137
$$ $$

## alpha138
$$ r1 = Rank(DecayLinear(Delta(low * 0.7 + vwap * 0.3,3),20))$$
$$ corr = Corr(TsRank(low,8),TsRank(Mean(volume,60),17),5)$$
$$ alpha138 = r1 - TsRank(DecayLinear(TsRank(corr,19),16),7)$$

## alpha139
$$ alpha139 = -1 * Corr(open,volume,10)$$

## alpha140
$$ temp = Rank(open) + Rank(low) -(Rank(high) + Rank(close))$$
$$ corr = Corr(TsRank(close,8),TsRank(Mean(volume,60),20),8)$$
$$ alpha140 = Min(Rank(DecayLinear(temp,8)),TsRank(DecayLinear(corr,7),3))$$

## alpha141
$$ alpha141 = -1 * Rank(Corr(Rank(high),Rank(Mean(volume,15)),9))$$

## alpha142
$$ r1 = Rank(TsRank(close,10)$$
$$ r2 = Rank(Delta(Delta(close,1),1))$$
$$ r3 = Rank(TsRank(\frac{volume}{Mean(volume,20)},5))$$
$$ alpha142 = -1 * r1 * r2 * r3$$

## alpha143
$$ alpha143 = \begin{cases}
				\frac{close - Delay(close,1)}{Delay(close,1)} * self,& close > Delay(close,1) \\\
				self,& else
				\end{cases}
				$$

## alpha144
$$ temp = \frac{abs(\frac{close}{Delay(close,1)}-1)}{amount}$$
$$ tep1 = SumIf(temp,20,close < Delay(close,1))$$
$$ tep2 = Count(close < Delay(close,1),20)$$
$$ alpha144 = \frac{tep1}{tep2}$$

## alpha145
$$ alpha145 = \frac{Mean(volume,9) - Mean(volume,26)}{Mean(volume,12)} * 100$$

## alpha146(??)
$$ temp1 = \frac{close - Delay(close,1)}{Delay(close,1)}$$
$$ temp2 = temp1 - SMA(temp1,61,2) $$
$$ alpha146 = \frac{Mean(temp2，20) * temp2}{SMA(temp1-temp2,61,2)}$$

## alpha147 
$$ alpha147 = RegBeta(Mean(close,12),sequence,12)$$

## alpha148
$$ r1 = Rank(Corr(open,Sum(Mean(volume,60),9),6))$$
$$ r2 = Rank(open - TsMin(open,14))$$
$$ alpha148 = (r1 < r2) * -1$$

## alpha149
$$ f1 = Filter(\frac{close}{Delay(close,1)}-1,benchClose < Delay(benchClose,1))$$
$$ f2 = Filter(\frac{benchClose}{Delay(benClose,1)}-1,benchClose < Delay(benchClose,1))$$
$$ alpha149 = RegBeta(f1,f2,252)$$

## alpha150
$$ alpha150 = \frac{close + high + low}{3} * volume$$

## alpha151
$$ alpha151 = SMA(close - Delay(close,20),20,1)$$

## alpha152
$$ temp = Delay(\frac{close}{Delay(close,9)},1)$$
$$ tep = Delay(SMA(temp,9,1),1)$$
$$ alpha152 = SMA(Mean(tep,12) - Mean(tep,26),9,1)$$

## alpha153
$$ alpha153 = \frac{Mean(close,3) + Mean(close,6) + Mean(close,12) + Mean(close,24)}{4}$$

## alpha154
$$ corr = Corr(vwap,Mean(volume,180),18)$$
$$ alpha154 = ((vwap - Min(vwap,16))< corr)$$

## alpha155
$$ temp = SMA(volume,13,2) - SMA(volume,26,2)$$
$$ alpha155 = temp - SMA(temp,10,2)$$

## alpha156
$$ r1 = Rank(DecayLinear(Delta(vwap,5),3))$$
$$ temp = Delta(open * 0.15 + low * 0.85,2) * -1$$
$$ alpha156 = -1 * Max(r1, Rank(DecayLinear(temp,3)))$$

## alpha157(??)
$$ r1 = TsMin(Rank(-1 * Rank(Delta(close,5))),2)$$
$$ r2 = TsRank(Delay(-1 * ret,6),5)$$
$$ alpha157 = Min(r1+r2, 5)$$

## alpha158
$$ temp = SMA(close,15,2)$$
$$ alpha158 = \frac{(high - temp) - (low - temp)}{close}$$

## alpha159
$$ temp1 = Min(low,Delay(close,1))$$
$$ temp2 = Max(high,Delay(close,1)) $$
$$ temp3 = \frac{Close - Sum(temp1,6)}{Sum(temp2-temp1,6)} * 12 * 24 + \frac{close - Sum(temp1,12)}{Sum(temp2 - temp1,12)} * 6 * 24 + \frac{close - Sun(temp1,24)}{Sum(temp2 - temp1,24)} * 6 * 24$$
$$ alpha159 = 100 * \frac{temp3}{6*12 + 6*24 + 12*24} $$

## alpha160
$$ alpha160 = \begin{cases}
				SMA(STD(close,20),20,1),&close < Delay(close,1)\\\
				SMA(0,20,1),& else
				\end{cases}
				$$

## alpha161
$$ temp1 = Max((high - low),abs(Delay(close,1) - high))$$
$$ temp2 = abs(Delay(close,1) - low)$$
$$ alpha161 = Mean(Max(temp1,temp2),12)$$

## alpha162
$$ temp1 = SMA(Max(close - Delay(close,1),0),12,1)$$
$$ temp2 = SMA(abs(close - Delay(close,1)),12,1)$$
$$ temp3 = Min(\frac{temp1}{temp2} ,12)$$
$$ temp4 = Max(\frac{temp1}{temp2} ,12)$$
$$ alpha162 = (\frac{temp1}{temp2}  - \frac{temp3}{temp4}) * 100  $$

## alpha163
$$ alpha163 = Rank(-1 * ret * Mean(volume,20) * vwap * (high - close))$$

## alpha164 
$$ temp = \begin{cases}
				\frac{1}{close - Delay(close,1)} - \frac{Min(\frac{1}{close - Delay(close,1)},12)}{high - low} ,& close > Delay(close,1)\\\
				0, & else
				\end{cases}
				$$
$$ alpha164 = SMA(temp * 100,13,2)$$

## alpha165
$$ temp = SUMAC(close - Mean(close,48))$$
$$ alpha165 = \frac{Max(temp) - Min(temp)}{STD(close,48)}$$

## alpha166(??)
$$ temp1 = \frac{close}{Delta(close,1)}$$
$$ temp2 = 20 * (20 - 1) * Sum(temp1 - Mean(temp1,20))$$
$$ temp3 = (20 -1) * (20 -2) * Sum(temp1,20)$$

## alpha167
$$ temp = \begin{cases}
			close - Delay(close,1),& close > Delay(close,1) \\\
			0,& else
			\end{cases}
			$$
$$ alpha167 = Sum(temp,12)$$

## alpha168
$$ alpha168 = -1 * \frac{volume}{Mean(volume,20)}$$

## alpha169
$$ temp1 = close - Delay(close,1)$$
$$ temp2 = Delay(SMA(temp1,9,1),1)$$
$$ alpha169 = SMA(Mean(temp2,12) - Mean(temp2,26),10,1)$$

## alpha170(??)
$$ r1 = Rank(\frac{high}{close} * \frac{volume}{Mean(volume,20)})$$
$$ r2 = Rank(\frac{high - close}{Mean(high,5)}) - Rank(vwap -  Delay(vwap,5))$$
$$ alpha170 = r1 * r2$$

## alpha171
$$ alpha171 = -1 *\frac{(low - close) * (open ^ 5)}{(close - high)*(close ^ 5)}$$

## alpha172
$$ temp = \begin{cases}
				1, &(LD>0,LD>HD) OR (HD>0,HD>LD) \\\$$
				0, else
			\end{cases}
### another
$$ temp = \begin{cases}
				1, &(LD>0,LD>HD) OR )\\\
				-1, & (HD>0,HD>LD) \\\$$
				0, else
			\end{cases}
$$ alpha172 = Mean(temp,6)$$

## alpha173(?)
$$ temp1 = SMA(close,13,2)$$
$$ temp2 = SMA(Ln(close),13,2)$$
$$ alpha173 = 3 * temp1 - 2 * SMA(temp1,13,2) + SMA(SMA(temp2,13,2),13,2)$$

## alpha174
$$ alpha174 = \begin{cases}
				SMA(STD(close,20),20,1),& close > Delay(close,1) \\\
				SMA(0,20,1),else
				\end{cases}
				$$

## alpha175
$$ temp1 = Max(high - low, abs(Delay(close,1) - high))$$
$$ temp2 = Max(temp1,abs(Delay(close,1) - low))$$
$$ alpha175 = Mean(Max(temp1,temp2),6)$$

## alpha176
$$ r1 =Rank(\frac{close - TsMin(low,12)}{TsMax(high,12) - TsMin(low,12)}) $$
$$ r2 = Rank(volume)$$
$$ alpha176 = Corr(r1,r2,6)$$

## alpha177
$$ alpha177 = \frac{20 - Highday(high,20)}{20} * 100$$

## alpha178
$$ alpha178 =\frac{close - Delay(close,1)}{Delay(close,1)} * volume$$

## alpha179
$$ r1 = Rank(Corr(vwap,volume,4))$$
$$ corr = Corr(Rank(low),Rank(Mean(volume,50)),12)$$
$$ alpha179 = r1 * Rank(corr)$$

## alpha180
$$ alpha180 = \begin{cases}
				-1 * TsRank(abs(Delta(close,7)),60) * Sign(Delta(close,7)), & Mean(volume,20) < volume\\\
				-1 * volume,& else
				\end{cases}
				$$

## alpha181
$$ temp1 = \frac{close}{Delay(close,1)}$$
$$ temp2 =  temp1 - Mean(temp1,20)$$
$$ temp3 = benchClose - Mean(benchClose,20)$$
$$ alpha181 = \frac{Sum(temp2 - temp3)^2}{Sum(temp2)^3}$$

## alpha182
$$ temp1 = (close > open AND benckClose > benchOpen)$$
$$ temp2 = (close < open AND benchClose < benchOpen)$$
$$ alpha182 = \frac{Count(temp1 OR temp2,20)}{20} $$

## alpha183
$$ temp = close - Mean(close,24)$$
$$ alpha183 = \frac{Max(MAXAC(temp)) - Min(MINAC(temp))}{STD(close,24)}$$

## alpha184
$$ r1 = Rank(Corr(Delay(open - close,1),close,200))$$
$$ r2 = Rank(open - close)$$
$$ alpha184 = r1 + r2$$

## alpha185
$$ alpha185 = Rank(-1 * (1 - \frac{open}{close})^2)$$

## alpha186
$$ temp = \begin{cases}
				1, &(LD>0,LD>HD) OR (HD>0,HD>LD) \\\$$
				0, else
			\end{cases}
$$ alpha186 = \frac{Mean(temp,6) + Delay(Mean(temp,6),6)}{2}$$

## alpha187
$$ alpha187 = \begin{cases}
					0, &open <= Delay(open,1) \\\
					Sum(Max(high - open,open - Delay(open,1)),20),& else
					\end{cases}
					$$

## alpha188
$$ temp = SMA(high -low,11,2)$$
$$ alpha188 = \frac{high - low - temp}{temp} * 100$$

## alpha189
$$ alpha189 = Mean(abs(close - Mean(close,6)),6)$$

## alpha190
$$ $$

## alpha191
$$ alpha191 = Corr(Mean(volume,20),low,5) + \frac{high + low}{2} - close$$





