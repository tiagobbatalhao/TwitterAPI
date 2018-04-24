import twitter
import Tokens
import time
import datetime
import sklearn.neighbors
import pylab as py

t = twitter.Twitter(auth=twitter.OAuth(
    Tokens.token,
    Tokens.token_secret,
    Tokens.consumer_key,
    Tokens.consumer_secret))

def search_hashtag(hashtag, limit = 10000, geo=False, **kwargs):
    args = {}
    args['q'] = '#' + hashtag
    args['result_type'] = 'recent'
    args['count'] = 10
    args['include_entities'] = 'true'
    args.update(kwargs)
    max_id = args.get('max_id')
    if geo:
        coordinates_bauru = (-22.303074, -49.065628)
        args['geo'] = ','.join([str(x) for x in coordinates_bauru]+['450km'])
    status = []
    try:
        while len(status) < limit:
            if max_id:
                args['max_id'] = max_id
            query = t.search.tweets(**args)
            this = query['statuses']
            if len(this)==0:
                break
            status += list(this)
            max_id = status[-1]['id'] - 1
            print(len(status))
    except twitter.api.TwitterHTTPError:
        pass
    return status

def convert_to_epoch(tweet):
    str_time = tweet['created_at']
    str_format = '%a %b %d %H:%M:%S %z %Y'
    dt = datetime.datetime.strptime(str_time, str_format)
    return dt.timestamp()

def plot_rate(tweets, bandwidth=10, plot_interval=10):
    initial_day = 6
    total_days = 10

    tz = datetime.timezone(datetime.timedelta(hours=-3))
    initial_date = datetime.datetime(2018,4,initial_day,0,0,0,tzinfo=tz)
    initial_epoch = initial_date.timestamp()
    tweet_times = [convert_to_epoch(x)-initial_epoch for x in tweets]
    kde = sklearn.neighbors.KernelDensity(kernel='tophat',bandwidth=bandwidth*60)
    kde.fit(py.array(tweet_times).reshape(-1,1))

    total_interval = total_days * 24 * 3600
    points = int(total_interval / (60 * plot_interval))
    plot_x = py.linspace(0,total_interval,points,endpoint=False)

    plot_y = [3600*len(tweets)*py.exp(x) for x in kde.score_samples(plot_x.reshape(-1,1))]

    fig,ax = py.subplots()
    ax.plot(plot_x, plot_y, 'k-')

    ticks = [x*24*3600 for x in range(total_days+1)]
    labels = [str(x+initial_day) for x in range(total_days+1)]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.set_xlabel('Dia (abril/2018)')
    ax.set_ylabel('Tweets por hora')
    # ax.set_yticks([])

    return plot_x, plot_y, fig


def plot_tweets_day(tweets, day, bandwidth=10, plot_interval=10, title=None):
    tz = datetime.timezone(datetime.timedelta(hours=-3))
    initial_date = datetime.datetime.strptime(day+' -0300','%Y-%m-%d %z')
    initial_epoch = initial_date.timestamp()
    tweet_times = [convert_to_epoch(x)-initial_epoch for x in tweets]
    tweet_times_day = [x for x in tweet_times if x>=0 and x<24*3600]
    kde = sklearn.neighbors.KernelDensity(kernel='tophat',bandwidth=bandwidth*60)
    kde.fit(py.array(tweet_times_day).reshape(-1,1))

    total_interval = 24 * 3600
    points = int(total_interval / (60 * plot_interval))
    plot_x = py.linspace(0,total_interval,points,endpoint=False)
    plot_y = [3600*len(tweet_times_day)*py.exp(x) for x in kde.score_samples(plot_x.reshape(-1,1))]

    fig,ax = py.subplots()
    ax.plot(plot_x, plot_y, 'k-')

    ticks = [0,4,8,12,16,20,24]
    labels = ['{:02d}:00'.format(x) for x in ticks]
    ax.set_xticks([x*3600 for x in ticks])
    ax.set_xticklabels(labels)
    ax.set_xlabel('Hora')
    ax.set_ylabel('Tweets por hora')
    ax.set_title(title)
    # ax.set_yticks([])
    ax.set_ylim(0,600)
    ax.set_yticks([0,100,200,300])

    return plot_x, plot_y, fig
