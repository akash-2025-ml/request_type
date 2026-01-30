import redis

from auto import classify_email
import datetime

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def get_value(id):
    # strat = datetime.datetime.now()
    # print("#message_fetch_redis#start#" + str(strat))
    # r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # outp = r.get(id)
    # end = datetime.datetime.now()
    # print("#message_fetch_redis#end#" + str(end))
    # print("total time taken by redis = ", (end - strat))
    return classify_email(id)


# s = get_value(
#     """Hello Meera,

# I hope you’re doing well. I’m applying for the internal Data Lead position opening this quarter and would be grateful if you could provide a professional reference highlighting my contributions during the ModelOps initiative.

# You were my reporting manager during that project, so your recommendation would mean a lot.

# Thanks in advance,
# Aditya Sharma
# """)

# print(s)
