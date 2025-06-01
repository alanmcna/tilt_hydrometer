from flask import Flask, request, render_template, send_from_directory
import datetime

app = Flask(__name__)

OG = float('nan')
SLEEP = 360

def set_og(g):
    global OG
    OG = g


def get_sleep():
    global SLEEP
    return SLEEP


def set_sleep(s):
    global SLEEP
    SLEEP = s


def isNan(x):
    return ( x != x )


def calc_abv(g):
    global OG

    if isNan(OG):
        return OG
    # make sure it's not negative since sg can fluctuate ;)
    return abs((76.08 * (OG - g) / (1.775 - OG)) * (g / 0.794)) 


def calc_gravity(t, b):
    # best fit conversion
    return 0.958 + 0.00118 * t + 0.00000579 * t * t


def get_og():
    global OG

    if isNan(OG):
        with open('data/hydrometer.csv','r') as fd:
            # just make sure we're at the beginning
            fd.seek(0)
            line = fd.readline()
            d = line.split(',')
            if len(d) == 7:
                OG = float(d[5])
    return OG


def get_latest_g():
    with open('data/latest_hydrometer.csv','r') as fd:
        # just make sure we're at the beginning
        fd.seek(0)
        line = fd.readline()
        d = line.split(',')
        if len(d) == 7:
            return float(d[5])
    return get_og()

# -- web handlers --

@app.route('/data/<path:path>')
def send_data(path):
    return send_from_directory('data', path)


@app.route("/", methods = ['POST'])
def handle_post_index():
    data = request.get_json(force=True)

    if data and 'tilt' in data:
        t_az = 90 - abs(data['tilt']);
        g = calc_gravity(t_az, data['board'])
        t = datetime.datetime.now()

        line = "{},{},{},{},{},{},{}".format(t.strftime('%Y-%m-%d %H:%M:%S'), t_az, data['roll'], data['temp'], data['bv'], g, data['board'])
        print("debug: received from board {}: {}".format(data['board'], line))

        with open('data/hydrometer.csv','a') as fd:
            # if it's the first thing to be written it 'must' be the og, surely?
            if fd.tell() == 0:
                set_og(g)
            fd.write("{}\n".format(line))
        with open('data/latest_hydrometer.csv','w') as fd:
            fd.write("{}\n".format(line))

    return { 'OK': get_sleep() }


@app.route("/abv", methods = ['GET'])
def handle_get_abv():
    fg = get_latest_g()
    return { 'ABV': calc_abv(fg), 'OG': get_og(), 'FG': fg }


@app.route("/og", methods = ['GET'])
def handle_get_og():
    return { 'OG': get_og() }


@app.route("/sleep", methods = ['GET'])
def handle_get_sleep():
    return { 'SLEEP': get_sleep() }


@app.route("/sleep", methods = ['POST'])
def handle_post_sleep():
    data = request.get_json(force=True)

    if data and 'sleep' in data:
        set_sleep(data['sleep'])

    return { 'SLEEP': get_sleep() }


@app.route("/reset", methods = ['GET'])
def handle_get_reset():
    set_og(float('nan'))

    return { 'OG': get_og() }


@app.route("/", methods = ['GET'])
def handle_get_index():
    fg = get_latest_g()
    return render_template('index.html', abv=calc_abv(fg))


if __name__ == '__main__':
    get_og()
    app.run(host='0.0.0.0', port=80)
