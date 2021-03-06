head = """
	<link rel="stylesheet" type="text/css" href="../static/main.css" />	
	<link rel="stylesheet" type="text/css" href="../static/table.css" />
	<script src="../static/jquery.js"></script>
	<script type="text/javascript" src="../static/gdraw.js"></script>
	<script type="text/javascript">

      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-16398465-1']);
      _gaq.push(['_trackPageview']);

      (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();

    </script>
"""

responseDict = {
'adp_100' : 	'Average Daily Price - 100 day',
'adp_200'	:  	'Average Daily Price - 200 day',
'adp_50'	:  	'Average Daily Price - 50 day',
'adv_21'	:  	'Average Daily Volume - 21 day',
'adv_30'	:  'Average Daily Volume - 30 day',
'adv_90'	:  	'Average Daily Volume - 90 day',
'ask'	:    	'Ask price',
'ask_time'	:    	'Time of latest ask',
'asksz'	:    	"Size of latest ask (in 100's)",
'basis'	:    	'Reported precision (quotation decimal places)',
'beta'	:  	"Beta volatility measure",
'bid'	:    	"Bid price",
'bid_time'	:    	"Time of latest bid",
'bidsz'	:    	"Size of latest bid (in 100's)",
'bidtick'	:  	"Tick direction since last bid",
'chg'	:    	"Change since prior day close (cl)",
'chg_sign'	:    	"Change sign (e   u   d) as even   up   down",
'chg_t'	:    	"change in text format",
'cl'	:    	"previous close",
'contract_size'	  : 	"contract size for",
'cusip'	:  	'Cusip',
'date'	:    	'Trade date of last trade',
'datetime'	:    	'Date and time',
'days_to_expiration':	   	'Days until   expiration date',
'div'	:  	'Latest announced cash dividend',
'divexdate'	:  	'Ex-dividend date of div(YYYYMMDD)',
'divfreq'	:  	'Dividend frequency   Quarterly   Monthly   Yearly   etc.',
'divpaydt'	:  	'Dividend pay date of last announced div',
'dollar_value'	:    	'Total dollar value of shares traded today',
'eps'	:  	'Earnings per share',
'exch'	:    	'exchange code',
'exch_desc'	:    	'exchange description',
'hi'	:    	'High Trade Price for the trading day',
'iad'	:  	'Indicated annual dividend',
'idelta'	   :	  'risk measure of delta using implied volatility',
'igamma'	   :	  'risk measure of gamma using implied volatility',
'imp_volatility':	   	'Implied volatility of   price based current : price',
'incr_vl'	:    	'Volume of last trade',
'irho'	   	: 'risk measure of rho using implied volatility',
'issue_desc'	:   	'Issue description',
'itheta'    :	   	  'risk measure of theta using implied volatility',
'ivega'	  : 	  'risk measure of vega using implied volatility',
'last'	:    	'Last trade price',
'lo'	:    	'Low Trade Price for the trading day',
'name'	:    	'Company name',
'op_delivery'   :	'Settlement Designation - S Std N - Non Std X - NA',
'op_flag'	:  	'Security has (1=Yes   0=No).',
'op_style'	   	 : "Style - values are A American and E European",
'op_subclass'	  : 	  'class (0=Standard   1=Leap   3=Short Term)',
'openinterest'	  : 	'Open interest of   contract',
'opn'	:    	'Open trade price',
'opt_val'	   	: 'Estimated   Value - via Ju/Zhong or Black-Scholes',
'pchg'	:    'percentage change from prior day close',
'pchg_sign'	:    	"pchg sign   u for up   d for down",
'pcls'	:    	"Prior day close",
'pe'	:  	'Price earnings ratio',
'phi'	:    	'Prior day high value',
'plo'	:    	'Prior day low value',
'popn'	:    	'Prior day open',
'pr_adp_100'	:  	"Prior Average Daily Price 100 trade days",
'pr_adp_200'	:  	"Prior Average Daily Price 200 trade days",
'pr_adp_50'	:  	"Prior Average Daily Price 50 trade days",
'pr_date'	:    	"Trade Date of Prior Last",
'pr_openinterest'	:   	"Prior day's open interest",
'prbook'	:  	"Book Value Price",
'prchg'	:    	"Prior day change",
'prem_mult'	 :  	  "premium multiplier",
'put_call'	  : 	  "type (Put or Call)",
'pvol'	:    	"Prior day total volume",
'qcond'	 :  	"Condition code of quote",
'rootsymbol'	  : 	  "root symbol",
'secclass'	:    	"Security class (0=:   1= )",
'sesn'	:    	"Trading session as (pre   regular   &amp   post)",
'sho'	:  	"Shares Outstanding",
'strikeprice'	  : 	  "strike price (not extended by multiplier)",
'symbol'	:    	"Symbol from data provider",
'tcond'	:    	"Trade condition code - (H) halted or (R) resumed",
'timestamp'	:    	"Timestamp",
'tr_num'	:    	"Number of trades since market open",
'tradetick'	:    	"Tick direction from prior trade - (e  u  d) even   up   down)",
'trend'	:    	"Trend based on 10 prior ticks (e  u  d) even   up   down",
'under_cusip':	   	"An  's underlying cusip",
'undersymbol':	   "An  's underlying symbol",
'vl'	:    	"Cumulative volume",
'volatility12'	:  	"one year volatility measure",
'vwap'	:    	"Volume weighted average price",
'wk52hi'	:    	"52 week high",
'wk52hidate'	:    	"52 week high date",
'wk52lo'	:    	"52 week low",
'wk52lodate'	:    "52 week low date",
'xdate'	  : 	"Expiration date of   in the format of (YYYYMMDD)",
'xday'	   :	"Expiration day of ", 
'xmonth'	:   	"Expiration month of",
'xyear'	   	: "Expiration year of ",
'yield'	:  	"Dividend yield as %"
}