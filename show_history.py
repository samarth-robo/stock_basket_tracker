import enum

import dash
from app import start_app
from datetime import datetime
import json
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import yfinance as yf


class Stock(object):
  def __init__(self, name) -> None:
    self.name = name
    self.vis = True
    self.prices = []
    self.times = []
    self.vis_kwargs = {'mode': 'lines',
                       'line': {'width': 1,}}

  def get_data(self):
    print('Getting {:s} data'.format(self.name))
    self.times = np.asarray(list(range(10)))
    self.prices = np.random.uniform(0, 100, len(self.times))

  def basket_contribution(self, n, basket):
    contribs = np.zeros(len(self.prices))
    i0 = np.searchsorted(self.times, basket.times[0])
    assert(i0 >= 0)
    i1 = np.searchsorted(self.times, basket.times[-1])
    assert(i1 < len(self.times))
    contribs[i0:i1+1] = n*self.prices[i0:i1+1] / basket.prices
    return 100.0 * contribs

  @property
  def yields(self):
    return self.prices / self.prices[0]


class BasketTracker(object):
  def __init__(self, filename, start_date, end_date) -> None:
    self.start_date = start_date
    if end_date is not None:
      self.end_date = end_date
    else:
      self.end_date = datetime.today().strftime('%Y-%m-%d')
    
    with open(filename, 'r') as f:
      d = json.load(f)

    names = []
    self.n_shares = []
    for n,f in d.items():
      names.append(n)
      self.n_shares.append(int(f))
    self.stocks = [Stock(n) for n in names]
    self.dates = []
    self._get_data()
    # for s in self.stocks:
    #   s.get_data()

    self.fig = go.Figure()


  def _get_data(self):
    tickers = ' '.join([s.name for s in self.stocks])
    data = yf.download(tickers, start=self.start_date, end=self.end_date,
                       interval='1d')
    self.dates = [str(d).split(' ')[0] for d in data.index]
    min_time = len(self.dates)
    max_time = 0
    for s in self.stocks:
      p = data['Close', s.name].to_numpy()
      idx = np.isfinite(p)
      s.prices = p[idx]
      s.times = np.nonzero(idx)[0]
      if s.times[0] < min_time:
        min_time = s.times[0]
      if s.times[-1] > max_time:
        max_time = s.times[-1]
    # self.dates = [(i, all_dates[i]) for i in range(min_time, max_time+1)]
      
  
  def _calc_basket(self):
    b = Stock('basket')
    start_time = np.max([s.times[0]  for s in self.stocks])
    end_time   = np.min([s.times[-1] for s in self.stocks])
    b.times = np.asarray(list(range(start_time, end_time+1)))
    ps = []
    for s, n in zip(self.stocks, self.n_shares):
      i0 = np.searchsorted(s.times, start_time)
      assert(i0 > 0 or start_time==s.times[0])
      i1 = np.searchsorted(s.times, end_time)
      assert(i1 < len(s.times))
      ps.append(n * s.prices[i0:i1+1])
    b.prices = np.sum(np.vstack(ps), axis=0)
    b.vis_kwargs['line']['width'] = 4
    return b


  def _segment_dates(self):
    times = [0]
    dates = [self.dates[0]]
    for i in range(10, len(self.dates)-1):
      d0 = int(self.dates[i].split('-')[-1])
      d1 = int(self.dates[i+1].split('-')[-1])
      if d1 < d0:
        times.append(i+1)
        dates.append(self.dates[i+1])
    return times, dates

  
  def show(self):
    self.fig.data = []
    basket = self._calc_basket()
    for s, n in zip(self.stocks+[basket], self.n_shares+[1]):
      if not s.vis:
        continue
      name = s.name
      x = [self.dates[t] for t in s.times]
      self.fig.add_trace(go.Scatter(
        x=x,
        y=100.0*s.yields,
        name=name,
        text=[name for _ in range(len(x))],
        customdata=np.vstack((s.prices, s.basket_contribution(n, basket))).T,
        hovertemplate='<b>%{text}: %{y:.1f}%</b>, '+
                      '$%{customdata[0]:.1f}, '+
                      '%{customdata[1]:.1f}% of basket'+
                      '<extra></extra>',
        **s.vis_kwargs))
    tick_times, tick_dates = self._segment_dates()
    self.fig.update_layout(
      xaxis = dict(
        tickmode = 'array',
        tickvals = tick_dates,
        ticktext = tick_dates,
      ),
      legend = dict(
        xanchor='left',
        x=0,
        yanchor='bottom',
        y=1.02,
        orientation='h',
      ),
      title='Yields relative to start date, prices, and basket portions. {:s} to {:s}'.format(self.start_date, self.end_date),
      xaxis_title='Date',
      yaxis_title='Yield (%)'
    )
    start_app(self.fig)


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--ticker_names_file', required=True)
  parser.add_argument('--start_date', default='2015-01-01', help='YYYY-MM-DD')
  parser.add_argument('--end_date', default=None, help='Default today')
  args = parser.parse_args()

  bt = BasketTracker(args.ticker_names_file, args.start_date, args.end_date)
  bt.show()
