import clilib

test = [
    clilib.hourly_example("2019-01-23",
    11.1, 20, 8, 35, 15),
    clilib.hourly_example("2019-01-24",
    11.1, 20, 8, 35, 15),
    clilib.hourly_example("2019-01-25",
    11.1, 20, 8, 35, 15)
]



clilib.send_examples(test)