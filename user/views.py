from django.shortcuts import render
from .models import User
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np 
import pandas as pd 
import yfinance as yf


def many_line_chart(df,lists,name_block,title): 
    fig = go.Figure()
    for i,list in enumerate(lists):
        fig.add_trace(go.Scatter(x=df.index, y=list,
                        mode='lines',
                        name=name_block[i]))
    plot_div = fig.to_html(full_html=False)
    return plot_div

def many_subplots(dfs,lists,name_blocks,titles):
    fig = make_subplots(rows=1, cols=len(dfs))

    for i,(df,list,name_block,title) in enumerate(zip(dfs,lists,name_blocks,titles)):
        for int,lis in enumerate(list):
            if int==0:
                fig.add_trace(go.Scatter(x=df.index, y=lis,
                    mode='lines',
                    name=name_block[int]))
            if int>0: # we used first before
                new_line = go.Scatter(x=df.index, y=lis,
                    mode='lines',
                    name=name_block[int])
                fig.add_trace(new_line, row=1, col=i)

    plot_div = fig.to_html(full_html=False)
    return plot_div

# get all nasdaq tickets
df_tickets = pd.read_csv('nasdaq_screener.csv')
tickets = df_tickets.Symbol.values

all_titles = tickets[:21] # It doesn't take much to test the work

block = [] 
for ticket in all_titles: # get data to choose the best and the worst
    df = yf.download(ticket, period = '1y', interval='1d') 
    block.append(df)

#find best
moves = []
for d in block:
    move = (d.iloc[-1]['Close'] - d.iloc[-6]['Close'])*100/d.iloc[-6]['Close']
    moves.append(move)
moves = np.array(moves)
arg_sort_moves = np.argsort(moves)

best_five = arg_sort_moves[-5:] 

# create a portfolio
portfolio_tickets = ['VUG','GLD'] #TLT  VTV LQD
proportion = [0.5,0.5]
list_df_portfolio = []
for ticket in portfolio_tickets: # get data to choose the best and the worst
    df = yf.download(ticket, period = '17y', interval='1d') 
    list_df_portfolio.append(df)

invest_sum = 10000

for i,(df,pr ) in enumerate(zip(list_df_portfolio,proportion)):    
    cl = df.Close.values
    start_shares = round(invest_sum* pr/cl[0],2)
    c = np.array(cl)
    if i==0:
        res = c*start_shares 
    else:
        res += c*start_shares

sp500 = yf.download('^GSPC', period = '17y', interval='1d') # for comparison 

def index(request):
    users = User.objects.order_by('age').values_list('name')
    youngest_user = users[0]

    x1 = [1,2,3,4]
    y1 = [30,25,31,43]

    sp = sp500.Close.values
    mltp = invest_sum/sp[0]
    print('len(res) : ',len(res),'len(sp) : ',len(sp),'sp[-6:] : ',sp[-6:])
    sp = np.array(sp)*mltp
    portf_div = many_line_chart(sp500,[res,sp],['Traders portfolio','S&P 500'],'Traders portfolio and S&P 500')
    best_titles = []  
    best_list = [] 
    for ind in best_five:
        ll = block[int(ind)]
        best_list.append(ll)
        tt = all_titles[int(ind)]
        best_titles.append(tt) 
  
    dfs = [sp500,block[best_five[-1]]]
    lists = [[res,sp],best_list]
    name_blocks = [['Traders portfolio','S&P 500'],best_titles]
    titles = ['Traders portfolio and S&P 500','Best 5 shares']

    #portf_div2 =  many_subplots(dfs,lists,name_blocks,titles)

    def scatter(x1,y1):
        trace = go.Scatter(x=x1,y=y1)
        layout = dict(
            title='Simple graph',
            xaxis=dict(range=[min(x1),max(x1)]),
            yaxis=dict(range=[min(y1),max(y1)])
        )

        fig = go.Figure(data=[trace],layout = layout)
        plot_div = fig.to_html(full_html=False)
        return plot_div


    context = {'youngest_user': youngest_user,'plot': scatter(x1,y1),'plot2': portf_div,'plot3':portf_div
              }

    return render(request, 'user/index.html', context) # templates/user/index.html worked 
    