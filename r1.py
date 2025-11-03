import redis


r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

r.set(
    "other",
    """Hello Meera,

I hope you’re doing well. I’m applying for the internal Data Lead position opening this quarter and would be grateful if you could provide a professional reference highlighting my contributions during the ModelOps initiative.

You were my reporting manager during that project, so your recommendation would mean a lot.

Thanks in advance,
Aditya Sharma
""",
)

print("Done")
